export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "GET") return res.status(405).json({ ok: false });
  const token = String(req.query?.token || "");
  if (!process.env.SMOKE_TEST_TOKEN || token !== process.env.SMOKE_TEST_TOKEN) {
    return res.status(404).json({ ok: false });
  }

  const key = process.env.OPENAI_API_KEY;
  if (!key) return res.status(200).json({ ok:false, stage:"config", message:"missing key" });

  const headers = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json"
  };

  try {
    const moderation = await fetch("https://api.openai.com/v1/moderations", {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: "omni-moderation-latest",
        input: "a clear glass of water"
      }),
      cache: "no-store"
    });
    const moderationData = await moderation.json().catch(() => ({}));
    if (!moderation.ok) {
      return res.status(200).json({
        ok:false,
        stage:"moderation",
        status:moderation.status,
        code:moderationData?.error?.code || null,
        type:moderationData?.error?.type || null,
        message:String(moderationData?.error?.message || "").slice(0,180)
      });
    }

    const image = await fetch("https://api.openai.com/v1/images/generations", {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: "gpt-image-2.5-flare",
        prompt: "Create one photorealistic communication-card picture of a clear glass of water centered on a clean white background. No words, logos, labels, people, or extra props. Square composition.",
        n: 1,
        size: "1024x1024",
        quality: "medium",
        output_format: "webp",
        output_compression: 90,
        background: "opaque",
        moderation: "auto"
      }),
      cache: "no-store"
    });
    const imageData = await image.json().catch(() => ({}));
    return res.status(200).json({
      ok:Boolean(image.ok && imageData?.data?.[0]?.b64_json),
      stage:"image",
      status:image.status,
      hasImage:Boolean(imageData?.data?.[0]?.b64_json),
      code:imageData?.error?.code || null,
      type:imageData?.error?.type || null,
      message:String(imageData?.error?.message || "").slice(0,180)
    });
  } catch (error) {
    return res.status(200).json({
      ok:false,
      stage:"exception",
      name:error?.name || null,
      message:String(error?.message || "").slice(0,180)
    });
  }
}
