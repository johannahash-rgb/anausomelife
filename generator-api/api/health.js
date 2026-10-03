export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  res.status(200).json({
    ok: true,
    service: "An Ausome Life image service",
    configured: Boolean(
      process.env.OPENAI_API_KEY &&
      process.env.UPSTASH_REDIS_REST_URL &&
      process.env.UPSTASH_REDIS_REST_TOKEN &&
      process.env.RATE_LIMIT_SALT
    )
  });
}
