# Code Reviewer Memory - Plane CLI

## Project Structure
- **Framework:** oclif 4 (TypeScript CLI framework)
- **Package:** `packages/cli/` within `plane-plugin` monorepo
- **Entry:** `src/index.ts` re-exports `@oclif/core` run
- **Commands:** `src/commands/{resource}/{action}.ts` pattern
- **Lib:** `src/lib/` (api, config, errors, output, prompts, issue-resolver, npm)
- **Types:** `src/types/` (plane.ts, config.ts)
- **Tests:** `test/` using mocha + chai + @oclif/test

## Known Issues (from 2026-03-03 review)
- `api.ts` `request()` always calls `res.json()` -- crashes on 204 No Content (DELETE ops)
- `config:init` access token prompt is broken (calls promptConfirm instead of promptAccessToken)
- `enableJsonFlag = true` on BaseCommand conflicts with manual `--json` flags on commands
- Several cycle commands missing `...BaseCommand.baseFlags` spread (no-input not parsed)
- `issue-resolver.ts` fetches ALL issues to find by sequence_id (perf issue)
- `stripHtml` duplicated 3x (output.ts, issue/get.ts, issue/update.ts)
- Mixed error handling: some use `process.exit(1)`, some use `this.error()`

## Conventions
- Config stored at `~/.planerc` with 0o600 permissions
- Destructive ops require `--confirm` flag
- Interactive prompts disabled via `--no-input`
- Zod schema validates config
- All API output is JSON when `--json` flag used

## Test Patterns
- `test/helpers/mock-api.ts` provides full PlaneAPI mock
- API tests mock `globalThis.fetch` directly
- Command tests use `@oclif/test` `runCommand()`
- Config tests use `PLANE_CONFIG_PATH` env var for isolation
