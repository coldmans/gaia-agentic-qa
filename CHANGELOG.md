# Changelog

All notable changes to this project are documented in this file.

## 0.2.0 - 2026-07-16

### Added

- Reproducible public Human vs GAIA suite materialization from the scenario manifest.
- A responsive portfolio case study deployed separately from the capstone demo.
- Pure presentation-log classification helpers with focused GUI tests.
- A dependency lockfile for reproducible development and release validation.

### Changed

- Codex OAuth now delegates exclusively to the installed Codex CLI and never copies access or refresh tokens into GAIA state.
- The public benchmark example and report use GPT-5.6 Sol.
- The portfolio homepage reports the latest 26 SUCCESS / 4 blocked / 0 agent FAIL regression result instead of presenting the historical 30/30 baseline as current.

### Verified

- 731 Python unit tests.
- Next.js lint and production build.
- 30-scenario GPT-5.6 Sol live-site regression plus blocked-only rerun.
- Mobile viewport and production Vercel deployment.
