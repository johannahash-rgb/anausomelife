# An AUsome Life studio API — deployed candidate, generation disabled

This directory is the **intended Vercel project root for the outing research service**. The concurrently added `generator-api` package is a separate, still-disabled picture-card candidate. The main `anausomelife.com` website stays on GitHub Pages. Do not import or deploy the repository root, change its domain, or replace its hosting.

## Current state

The isolated service was deployed on 3 October 2026 after the owner authorized the official Vercel CLI device flow. The ChatGPT Vercel connector still returned an empty team list and a team-scope 403 after reconnection; CLI access succeeded for the same workspace. No website JavaScript calls the service, and generation is disabled. No OpenAI or Redis credentials are configured, and those providers have not been tested live. See `../../docs/studio-api-deployment-2026-10-03.md` for verified deployment details and remaining setup.

## Request and release flow

`POST /api/generate` receives JSON `{ "destination": "L.L.Bean, Freeport, Maine", "context": "A short visit and a quiet break" }`. It accepts no uploads, arbitrary URLs, provider settings or extra fields. Supported origins are the two main-site origins.

1. Atomically reserve one of 10 daily service attempts and 3 hourly attempts per hashed network address. Redis outages fail closed. Counters expire within 48 hours, network hashes change daily, and raw addresses are not written to Redis.
2. Moderate the text and enforce the owner's stricter family-friendly policy.
3. Research public sources; stop for ambiguous destinations. Source URLs must occur in the actual provider search/citation output. Treat every web page and supplied request as untrusted data.
4. Moderate the researched story/visual brief. Generate one original, people-free editorial image with default provider moderation.
5. Moderate the completed image and text, and apply the stricter visual policy check. Only then return a result with a unique ID, source links, retrieval date and an explicit AI-image caption. Nothing streams before the checks finish.

Failures return a short recoverable message without raw provider errors, prompts or secrets. There is no gallery, persistent image store, automatic retry, or application logging of requests. Infrastructure/provider retention must be described accurately before public activation. Classifiers and source checks reduce risk; they do not guarantee legality, accuracy or perfect moderation.

## Deployment boundary and remaining configuration

- Project name: `anausomelife-studio-api`, workspace `johannahash-3896`.
- Repository: `johannahash-rgb/anausomelife`; **local deployment directory: `services/studio-api`**. Git integration is not connected. If enabled later, explicitly set the repository Root Directory to `services/studio-api` before accepting automatic deployments.
- Framework: Other; Node.js 24; no dependencies or build step; Vercel Functions.
- Keep `STUDIO_ENABLED=false` during setup. Vercel classified the first deployment as production despite an explicit preview target; the separate service remained disabled and its deployment URL retained Vercel authentication protection. Health reports configuration state, not successful live provider verification.
- Only `public/` is served as static content. `.vercelignore` excludes local credentials, environment files and tests from deployment uploads. Function dependencies remain bundled server-side.
- Add private server variables from `.env.example` using a secure credential flow or the host's settings; never chat or public code. A text model supporting vision, structured output and web search is required; the image model must support the configured GPT Image parameters. Choose available models and review their current costs in the actual provider project.
- Redis uses the Upstash REST API and atomic Lua. Do not replace the limiter with in-memory counters on serverless instances.
- Configure provider/host budget controls, alerts and an emergency disable procedure before enabling public requests. The code's hard request caps bound attempts, not a dollar amount; calls and infrastructure can still incur costs.
- Verify actual search response shapes, provider availability/organization requirements, moderation decisions, output image handling, counter concurrency and duration before turning on.
- Add the public-site integration only after these live checks. Its submit action must disclose that destination/context go to Vercel and OpenAI, keep uploaded photos local, preserve existing edited work on failure, expose clarification choices, show source links and the AI caption, and have accessible progress/status messages. Update `privacy.html` at the same time. Do not claim live generation until this full browser → API → moderated output flow succeeds.

## Validation

Run `node test/safety.test.js` from this directory (18 tests). Tests use stubbed providers, not paid API calls. They cover withheld unsafe output, input rejection, moderation/network failures, ambiguity, unverified sources, invalid inputs, foreign origins, disabled configuration and exhausted counters. They do not validate real classifier accuracy or a live Redis deployment.

## Implementation references checked 3 October 2026

- https://developers.openai.com/api/docs/guides/tools-web-search
- https://developers.openai.com/api/docs/guides/moderation
- https://developers.openai.com/api/docs/guides/image-generation
- https://upstash.com/docs/redis/features/restapi
- https://vercel.com/docs/headers/request-headers
- https://vercel.com/docs/functions
