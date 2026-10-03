# Outing studio: research, then draw

Owner direction, 3 October 2026: any general location request should lead to internet research, an original gorgeous photorealistic image in the preppy Nantucket-meets-Vermont aesthetic, and a brief editable outing story. L.L.Bean is an example, not a limit on destinations.

## Current delivery

The GitHub Pages studio accepts free text, recognizes the 29 maintained destinations, adapts suggestions to everyday scenarios, offers optional wording/color/photo controls, and prints five editable steps. L.L.Bean has an original researched editorial image, explicitly labeled AI-created. Its real family reference photo remains separate in the activity step. Forty guide URLs share 29 short introductions and practical starting tips. General suggestions are disclosed as suggestions; unrecognized venues do not receive a fabricated venue photograph.

This release has **no live research or image API**. It does not claim to search the web or generate a new image when a visitor submits a request. The server connection is still required. Neither a chat image tool nor a connected Runway chat account automatically supplies a public website API.

## Required live flow

1. Receive a destination and optional town/context through a server, not a browser API key. Clearly disclose which text leaves the device; never upload the user's local photos automatically.
2. Validate length and type, apply abuse controls and a bounded budget. Moderate the input and enforce the owner's family-friendly policy before research or image calls. Unknown moderation outcomes stop the request.
3. Research public venue sources, prioritizing the official site. Preserve source URLs, retrieval date and provenance. Treat retrieved text as untrusted data; ignore instructions within it. Ask the visitor to choose when a place name has multiple plausible matches. Do not silently infer a private address or precise user location.
4. Return verified place identity, a few source-grounded visual facts and explicitly uncertain details. Exclude private persons, private residences, real-person likenesses, dubious venues and prohibited content. Never fabricate a family visit, current accessibility, quiet conditions, opening hours or route.
5. Create an original photorealistic editorial image from the approved visual brief. Default to preppy New England styling without changing recognizable landmarks. Use an original composition; no unlicensed copied photos or misleading claims that artwork is a current photo. Real arrival/entrance references remain distinct.
6. Moderate the completed image and story on the server before releasing either. Errors, missing checks or inconclusive results fail closed. Never stream unreviewed image previews. Provider moderation alone does not promise zero errors; apply the stricter site policy as well.
7. Return the artwork, two-sentence proposed-visit opening, five editable steps, source links and a visible AI-image caption. Use plain progress stages: “Finding your place”, “Creating your picture”, “Checking the result”. Preserve edited work if the request fails.
8. Offer regenerate only as an explicit action, with throttling and budget limits. No public gallery or automatic retention of personal request text. Do not log raw prompts or user photos.

## Connection needed

A private server host, protected search/image service credentials and enforced abuse/budget controls must be provisioned and verified before exposing live generation. Keep the current GitHub Pages hosting. No API key belongs in this public repository, site JavaScript, generated HTML or chat. The separate service at `services/studio-api` has default-off configuration, text-only input, sourced research, input/output moderation, a stricter family-content review, atomic rate limits and no application prompt/photo logging. Eighteen local tests cover its fail-closed orchestration and request boundaries. On 3 October 2026, the owner authorized Vercel CLI access and the isolated service was deployed with generation disabled. Live hosting checks confirmed health HTTP 200, generation HTTP 503 while disabled, and HTTP 404 for server source files. OpenAI and Redis credentials, live provider verification and the public website integration are still pending. The ChatGPT connector's separate team-scope authorization problem persists. See `studio-api-deployment-2026-10-03.md` and the service README for the remaining release gates.

Official implementation references checked 3 October 2026:
- https://developers.openai.com/api/docs/guides/tools-web-search
- https://developers.openai.com/api/docs/guides/image-generation
- https://developers.openai.com/api/docs/guides/moderation

Release gate: test ambiguous destinations, unfamiliar locations, stale/conflicting facts, hostile source text, disallowed input, output rejection, moderation outage, rate limits, provider timeout and keyboard/screen-reader recovery against the actual connected service. Local UI checks do not substitute for this gate.
