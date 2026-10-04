# An AUsome Life image service

Private Vercel serverless backend for the public GitHub Pages picture-card maker.

## Purpose

The public site must never contain an OpenAI API key. This service receives only the short text description needed to make a picture. Local photos remain in the visitor's browser and are not uploaded by this endpoint.

The service fails closed unless its release flag, OpenAI credential, privacy salt and declared Vercel WAF abuse-control mode are configured. The public release procedure also requires an active Vercel WAF rate-limit rule on `POST /api/generate-card`.

**Release candidate: not connected.** Keep `IMAGE_SERVICE_ENABLED=false` until live verification. This package is for picture cards; `services/studio-api` remains the separate outing research service. Neither package replaces GitHub Pages.

## Required environment variables

- `IMAGE_SERVICE_ENABLED` — keep `false` until all release checks pass
- `ABUSE_CONTROL_MODE=vercel-waf`
- `OPENAI_API_KEY`
- `RATE_LIMIT_SALT` — a long random server-only secret used to hash the Vercel-provided client IP before sending the anonymous `user` identifier to OpenAI

Optional:

- `ALLOWED_ORIGINS` — comma-separated; defaults to `https://anausomelife.com,https://www.anausomelife.com`

## Abuse control

Use Vercel WAF rate limiting on the image endpoint. The release gate is:

- path: `/api/generate-card`
- method: `POST`
- key: source IP
- algorithm: fixed window
- window: 10 minutes
- limit: 3 requests
- action: HTTP 429

Keep the application-level CORS, request-size, content-type and moderation checks in place. WAF is the enforceable request-rate control; the client-side UI is not a security boundary.

## Release steps

1. Deploy this folder as a separate Vercel project with Root Directory `generator-api`.
2. Add the private environment variables in Vercel; never commit them.
3. Add and publish the WAF rule above.
4. Confirm `/api/health` reports `configured: true`.
5. Verify CORS rejects other origins and the WAF returns 429 after the configured limit.
6. Test an allowed everyday picture, a disallowed request, and a provider-error path.
7. Only after those checks pass, set `IMAGE_SERVICE_ENABLED=true` and redeploy if Vercel requires it for the environment change.
8. In `communication-card-generator.html`, set the `ausome-image-api` meta value to the full `/api/generate-card` URL.
9. Update privacy copy to disclose that the text description is sent to the image service/OpenAI while uploaded photos remain local.
10. Re-run editorial-rights checks and live keyboard/screen-reader checks before treating generation as released.

The static page continues to use the explicit ChatGPT handoff while this service is not connected.
