# Studio service deployment — 3 October 2026

## Verified state

- Workspace: configured project workspace (see authenticated deployment settings).
- Project: `anausomelife-studio-api` (`prj_MUg5pCZkb3hjPRH091ujfnuoufKp`).
- Deployment: `dpl_5zY2YTSQZDHvJqXCQgdYRRzeY9mt`, READY.
- Project alias: https://anausomelife-studio-api.vercel.app
- Source: `services/studio-api` only, based on repository commit `07ad1aa` plus the static-output and deployment-ignore changes recorded with this note.
- Main website remains on GitHub Pages. No domain or DNS changes were made.

The owner completed the official CLI device authorization. The ChatGPT plugin remained unable to list teams or access this known workspace after reconnection; the official CLI could access it. Do not ask the owner to reconnect the plugin repeatedly as a prerequisite for CLI work.

`vercel link` created the project and attempted to connect GitHub, but Vercel rejected Git integration because a GitHub login connection was missing. Direct CLI deployment succeeded. Do not claim Git-push deployment is configured. Set repository Root Directory to `services/studio-api` if Git integration is later added.

The command requested `--target preview`; Vercel nevertheless classified the initial deployment as production and assigned the project alias. The returned deployment protection included `vercel_authentication`. No protection was disabled. Runtime `STUDIO_ENABLED=false` was explicitly supplied, and the service also fails closed when that flag or required credentials are absent.

## Checks performed

- All 18 local safety tests passed; these use mocked providers.
- Deployment dry run confirmed only the service directory was uploaded. Local `.env.local`, `.env.example`, `.vercel/`, tests and README were excluded.
- Static output is restricted to `public/`; server implementation files are not static assets.
- Authenticated hosted `GET /api/health`: HTTP 200, `configured:false`, `release:candidate`.
- Authenticated hosted `POST /api/generate` with the allowed site origin: HTTP 503 with a safe unavailable message. No image/research calls are made while disabled.
- Authenticated hosted `GET /lib/provider.js`: HTTP 404.
- Project environment listing contained no stored environment variables at the time of verification. The disabled flag was provided to the deployment itself.

## Remaining before live generation

Private OpenAI credentials and approved text/image models; Upstash Redis REST credentials; a private rate-limit secret; provider and host spending controls; live input/output moderation and source-shape tests; and accessible website integration with accurate privacy disclosures. Do not advertise the website as a live generator until the complete flow succeeds. The separate `generator-api/` picture-card candidate remains undeployed and disabled.

## CLI verification note

Vercel CLI 62.2.0 incorrectly forwarded `--global-config` and `--no-color` to system curl. Verification succeeded using the CLI's XDG data-directory support and omitting those flags from `vercel curl`. Credentials were kept in restricted temporary storage outside the repository. Never commit credentials, local environment files, or deployment-protection secrets.
