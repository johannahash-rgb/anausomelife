export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "GET") return res.status(405).json({ ok: false });
  const token = String(req.query?.token || "");
  if (!process.env.SMOKE_TEST_TOKEN || token !== process.env.SMOKE_TEST_TOKEN) {
    return res.status(404).json({ ok: false });
  }

  try {
    const response = await fetch("https://anausomelife-image-service.vercel.app/api/generate-card", {
      method: "POST",
      headers: {
        "Origin": "https://anausomelife.com",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        subject: "a clear glass of water",
        situation: "communication card for asking for water"
      }),
      cache: "no-store"
    });
    const data = await response.json().catch(() => ({}));
    return res.status(200).json({
      ok: Boolean(response.ok && data.imageDataUrl),
      upstreamStatus: response.status,
      hasImage: Boolean(data.imageDataUrl),
      imageDataLength: data.imageDataUrl ? data.imageDataUrl.length : 0,
      description: data.description || null,
      message: data.message || null
    });
  } catch (_) {
    return res.status(200).json({
      ok: false,
      upstreamStatus: null,
      hasImage: false,
      imageDataLength: 0,
      description: null,
      message: "smoke test request failed"
    });
  }
}
