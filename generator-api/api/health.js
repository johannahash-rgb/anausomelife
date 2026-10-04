export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  res.status(200).json({
    ok: true,
    service: "An AUsome Life image service",
    configured: Boolean(
      process.env.IMAGE_SERVICE_ENABLED === "true" &&
      process.env.ABUSE_CONTROL_MODE === "vercel-waf" &&
      process.env.OPENAI_API_KEY &&
      process.env.RATE_LIMIT_SALT
    )
  });
}
