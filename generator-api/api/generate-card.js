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

async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function openai(path, body, timeoutMs = 20000) {
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
  }, timeoutMs);
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
  if (!Array.isArray(payload?.results) || !payload.results.length) {
    throw new Error("moderation_unavailable");
  }
  return payload.results.every(result =>
    typeof result.flagged === "boolean" &&
    result.flagged === false &&
    result.categories &&
    !Object.values(result.categories).some(Boolean)
  );
}

async function imageIsAllowed(imageDataUrl, text) {
  const { response, payload } = await openai("moderations", {
    model: "omni-moderation-latest",
    input: [
      { type: "text", text },
      { type: "image_url", image_url: { url: imageDataUrl } }
    ]
  }, 30000);
  if (!response.ok) throw new Error("moderation_unavailable");
  if (!Array.isArray(payload?.results) || !payload.results.length) {
    throw new Error("moderation_unavailable");
  }
  return payload.results.every(result =>
    typeof result.flagged === "boolean" &&
    result.flagged === false &&
    result.categories &&
    !Object.values(result.categories).some(Boolean)
  );
}

function makePrompt(subject, situation) {
  return [
    "Create one photorealistic communication-card picture.",
    `Requested subject: ${subject}.`,
    situation ? `Situation for context only: ${situation}.` : "",
    "An AUsome Life aesthetic: refined Nantucket meets Vermont, warm natural daylight, restrained coastal navy, cream and pine green only where naturally appropriate.",
    "Show one clearly recognizable everyday object or one simple action. Keep the subject centered on a clean light background with generous breathing room.",
    "Preserve the subject's real-world colors and recognizable shape. No words, letters, logos, labels, borders, collage, watermark or decorative clutter.",
    "Do not imitate a real identifiable person, celebrity, copyrighted character, branded product, private residence, published photograph, specific artist, or protected artwork. If the request suggests one, create an original generic unbranded alternative with no identifiable real person.",
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
  if (!contentType.includes("application/json")) {
    return res.status(415).json({ message: "Send this request as JSON." });
  }

  const length = Number(req.headers["content-length"] || 0);
  if (length > 5000) return res.status(413).json({ message: "That request is too long." });

  if (
    process.env.IMAGE_SERVICE_ENABLED !== "true" ||
    process.env.ABUSE_CONTROL_MODE !== "vercel-waf"
  ) {
    return res.status(503).json({ message: "The picture service is not enabled yet." });
  }

  try {
    const input = bodyFrom(req);
    const subject = cleanText(input.subject, 300);
    const situation = cleanText(input.situation, 600);
    if (!subject) return res.status(400).json({ message: "Describe the picture you want first." });

    const moderationText = [subject, situation].filter(Boolean).join("\n");
    if (!(await textIsAllowed(moderationText))) {
      return res.status(400).json({ message: "Please choose a generic, family-friendly everyday object, action or place." });
    }

    const { response, payload } = await openai("images/generations", {
      model: "gpt-image-2.5-flare",
      prompt: makePrompt(subject, situation),
      n: 1,
      size: "1024x1024",
      quality: "medium",
      output_format: "webp",
      output_compression: 90,
      background: "opaque",
      moderation: "auto"
    }, 100000);

    if (!response.ok) {
      if (payload?.error?.code === "moderation_blocked") {
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
