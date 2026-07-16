# Authentication boundary

GAIA supports two distinct OpenAI authentication paths.

## Codex OAuth (default)

1. `gaia auth login --provider openai --method oauth` runs the official
   `codex login` command.
2. GAIA checks the session with `codex login status`.
3. LLM requests are sent through `codex app-server`, with `codex exec` as the
   transport fallback.

GAIA does **not** read Codex Keychain entries or `~/.codex/auth.json`. It does
not copy access tokens, refresh tokens, or an API key into
`~/.gaia/auth/profiles.json` or `OPENAI_API_KEY`. The only value passed inside
GAIA is the non-secret sentinel `__gaia_codex_cli__`, which selects the Codex
transport.

Older GAIA versions copied Codex OAuth credentials into the GAIA profile. When
the current version encounters such an `oauth*` OpenAI profile, it deletes that
legacy copy and asks Codex for session status instead.

## Direct API key (explicit fallback)

`gaia auth login --provider openai --method manual` stores a user-supplied API
key in the local GAIA profile. `OPENAI_API_KEY` may also be supplied directly
through the process environment. This path calls the OpenAI API client and is
kept separate from Codex OAuth.

## Trust boundary

| Component | Owns credentials | GAIA can read raw credential |
| --- | --- | --- |
| Codex CLI OAuth | Codex CLI | No |
| OpenAI API key | User / GAIA local profile | Yes, only in manual mode |
| Gemini API key | User / GAIA local profile or env file | Yes |
| Vertex AI ADC | Google auth tooling | No service-account token copy |

Tests in `gaia/tests/unit/test_codex_auth.py` and
`gaia/tests/unit/test_auth.py` guard the no-copy contract.
