import { createHash } from "node:crypto";

const DEFAULT_ORIGINS = [
  "https://anausomelife.com",
  "https://www.anausomelife.com"
];

const SITE_BLOCK = /\b(porn(?:ography|ographic)?|nudes?|naked|sexual(?:ized|isation|ization)?|erotic|fetish|gore|gory|dismember(?:ment|ed)?|behead(?:ing|ed)?|tortur(?:e|ing)|swastika|nazi|deepfake|revenge porn)\b/i;

function allowedOrigins() {
  return new Set(
    (process.env.ALLOWED_ORIGINS || DEFAULT_ORIGINS.join(","))
      .split(",")
      .map(v => v.trim())
      .filter(Boolean)
  );
}

function applyCors(req, res) {
  const origin = String(req.headers.origin || "");
  if (!allowedOrigins().has(origin)) return false;
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Vary", "Origin");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Max-Age", "600");
  return true;
}

function bodyFrom(req) {
  if (typeof req.body === "string") return JSON.parse(req.body || "{}");
  return req.body || {};
}

function cleanText(value, max) {
  return String(value || "").replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, max);
}

function clientIp(req) {
  const forwarded = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return forwarded || String(req.headers["x-real-ip"] || "unknown");
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function redis(command) {
  const base = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!base || !token) throw new Error("rate_limit_unconfigured");
  const url = base.replace(/\/$/, "") + "/" + command.map(v => encodeURIComponent(String(v))).join("/");
  const response = await fetchWithTimeout(url, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store"
  }, 8000);
  if (!response.ok) throw new Error("rate_limit_unavailable");
  const payload = await response.json();
  return payload.result;
}

async function enforceLimits(req) {
  const salt = process.env.RATE_LIMIT_SALT;
  if (!salt) throw new Error("rate_limit_unconfigured");
  const hash = createHash("sha256").update(clientIp(req) + salt).digest("hex");
  const hourKey = `aal:image:hour:${hash}`;
  const hourCount = Number(await redis(["incr", hourKey]));
  if (hourCount === 1) await redis(["expire", hourKey, "3600"]);
  const perHour = Math.max(1, Math.min(20, Number(process.env.PER_IP_HOURLY_LIMIT || 4)));
  if (hourCount > perHour) return { ok: false, status: 429 };

  const day = new Date().toISOString().slice(0, 10);
  const dayKey = `aal:image:day:${day}`;
  const dayCount = Number(await redis(["incr", dayKey]));
  if (dayCount === 1) await redis(["expire", dayKey, "172800"]);
  const daily = Math.max(1, Math.min(500, Number(process.env.DAILY_IMAGE_LIMIT || 60)));
  if (dayCount > daily) return { ok: false, status: 429 };

  return { ok: true, user: hash.slice(0, 64) };
}

async function openai(path, body) {
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error("openai_unconfigured");
  const response = await fetchWithTimeout(`https://api.openai.com/v1/${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body),
    cache: "no-store"
  }, path === "images/generations" ? 100000 : 20000);
  const payload = await response.json().catch(() => ({}));
  return { response, payload };
}

async function textIsAllowed(text) {
  if (SITE_BLOCK.test(text)) return false;
  const { response, payload } = await openai("moderations", {
    model: "omni-moderation-latest",
    input: text
  });
  if (!response.ok) throw new Error("moderation_unavailable");
  if (!Array.isArray(payload?.results) || !payload.results.length || !payload.results.every(r => typeof r.flagged === "boolean" && r.categories && typeof r.categories.sexual === "boolean" && Object.values(r.categories).every(v => typeof v === "boolean"))) throw new Error("moderation_unavailable");
  return payload.results.every(r => !r.flagged && !Object.values(r.categories).some(Boolean));
}

async function imageIsAllowed(imageDataUrl, text) {
  const { response, payload } = await openai("moderations", {
    model: "omni-moderation-latest",
    input: [
      { type: "text", text },
      { type: "image_url", image_url: { url: imageDataUrl } }
    ]
  });
  if (!response.ok) throw new Error("moderation_unavailable");
  if (!Array.isArray(payload?.results) || !payload.results.length || !payload.results.every(r => typeof r.flagged === "boolean" && r.categories && typeof r.categories.sexual === "boolean" && Object.values(r.categories).every(v => typeof v === "boolean"))) throw new Error("moderation_unavailable");
  return payload.results.every(r => !r.flagged && !Object.values(r.categories).some(Boolean));
}

function makePrompt(subject, situation) {
  return [
    "Create one photorealistic communication-card picture.",
    `Requested subject: ${subject}.`,
    situation ? `Situation for context only: ${situation}.` : "",
    "An AUsome Life aesthetic: refined Nantucket meets Vermont, warm natural daylight, restrained coastal navy, cream and pine green only where naturally appropriate.",
    "Show one clearly recognizable everyday object or one simple action. Keep the subject centered on a clean light background with generous breathing room.",
    "Preserve the object's real colors and recognizable shape. No words, letters, logos, labels, borders, collage, watermark or decorative clutter.",
    "Do not imitate a real identifiable person, celebrity, copyrighted character, branded product, private residence, or published photograph. If the request depends on one, create an original generic unbranded alternative with no identifiable real person.",
    "All-ages, respectful, non-deceptive, calm and practical. Disability must never be portrayed as spectacle.",
    "Square composition. Realistic photographic detail, not cartoon, watercolor or clip art."
  ].filter(Boolean).join(" ");
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");

  if (!applyCors(req, res)) {
    return res.status(403).json({ message: "This image service is only available from An Ausome Life." });
  }
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ message: "Method not allowed." });

  const contentType = String(req.headers["content-type"] || "").toLowerCase();
  if (!contentType.includes("application/json")) return res.status(415).json({ message: "Send this request as JSON." });

  const length = Number(req.headers["content-length"] || 0);
  if (length > 5000) return res.status(413).json({ message: "That request is too long." });

  if (process.env.IMAGE_SERVICE_ENABLED !== "true") return res.status(503).json({ message: "The picture service is not enabled yet." });

  try {
    const limits = await enforceLimits(req);
    if (!limits.ok) {
      return res.status(limits.status).json({ message: "The picture studio has reached its current limit. Please try again later." });
    }

    const input = bodyFrom(req);
    const subject = cleanText(input.subject, 300);
    const situation = cleanText(input.situation, 600);
    if (!subject) return res.status(400).json({ message: "Describe the picture you want first." });

    const moderationText = [subject, situation].filter(Boolean).join("\n");
    if (!(await textIsAllowed(moderationText))) {
      return res.status(400).json({ message: "Please choose a family-friendly everyday object, action or place." });
    }

    const prompt = makePrompt(subject, situation);
    const { response, payload } = await openai("images/generations", {
      model: "gpt-image-2.5-flare",
      prompt,
      n: 1,
      size: "1024x1024",
      quality: "medium",
      output_format: "webp",
      output_compression: 90,
      background: "opaque",
      moderation: "auto",
      user: limits.user
    });

    if (!response.ok) {
      const code = payload?.error?.code;
      if (code === "moderation_blocked") {
        return res.status(400).json({ message: "Please try a different family-friendly picture request." });
      }
      return res.status(503).json({ message: "The picture service is temporarily unavailable." });
    }

    const b64 = payload?.data?.[0]?.b64_json;
    if (!b64) return res.status(503).json({ message: "The picture service did not return an image." });

    const imageDataUrl = `data:image/webp;base64,${b64}`;
    if (!(await imageIsAllowed(imageDataUrl, moderationText))) {
      return res.status(400).json({ message: "That result was not released. Please try a simpler everyday picture." });
    }

    return res.status(200).json({
      imageDataUrl,
      description: subject
    });
  } catch (_) {
    return res.status(503).json({ message: "The picture service is temporarily unavailable." });
  }
}
