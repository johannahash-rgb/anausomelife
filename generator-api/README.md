# An AUsome Life image service

Private Vercel serverless backend for the public GitHub Pages picture-card maker.

## Purpose

The public site must never contain an OpenAI API key. This service receives only the short text description needed to make a picture. Local photos remain in the visitor's browser and are not uploaded by this endpoint.

The service fails closed unless all required moderation and abuse-control infrastructure is configured.

**Release candidate: not connected.** Keep `IMAGE_SERVICE_ENABLED=false` until live verification. This package is for picture cards; `services/studio-api` is the separate outing research candidate. Neither package replaces GitHub Pages.

Before enabling this candidate, finish the stricter content-policy review, use a trusted Vercel client-IP header, verify atomic limits and provider timeout handling, and test failures with real services. A health response alone is not a release gate.

## Required environment variables

- `IMAGE_SERVICE_ENABLED` — keep `false` until all release checks pass
- `OPENAI_API_KEY`
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `RATE_LIMIT_SALT` — a long random secret used only to hash network addresses before rate-limit storage

Optional:

- `ALLOWED_ORIGINS` — comma-separated; defaults to `https://anausomelife.com,https://www.anausomelife.com`
- `PER_IP_HOURLY_LIMIT` — defaults to 4
- `DAILY_IMAGE_LIMIT` — defaults to 60

## Release steps

1. Deploy this folder as a separate Vercel project.
2. Add the required environment variables in Vercel; never commit them.
3. Confirm `/api/health` reports `configured: true`.
4. Verify CORS rejects other origins.
5. Test allowed, ambiguous, disallowed, rate-limited and provider-error requests.
6. Map a dedicated HTTPS host such as `https://image.anausomelife.com`.
7. Only after checks pass, enable the service. In `communication-card-generator.html`, set the `ausome-image-api` meta value to the full `/api/generate-card` URL.
8. Re-run the repository editorial-rights checks and live keyboard/screen-reader checks before treating generation as released.

The static page already falls back to a explicit ChatGPT handoff while this service is not connected.
