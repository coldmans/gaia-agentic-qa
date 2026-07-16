"""Local authentication helpers for GAIA.

Manual provider keys may be stored locally. OpenAI OAuth remains owned by the
Codex CLI and is never copied into GAIA storage or environment variables.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import argparse
import os
import getpass
import json
import re
import sys
import webbrowser
from typing import Any

from gaia.codex_auth import (
    CODEX_AUTH_SOURCE,
    CODEX_OAUTH_TOKEN_SENTINEL,
    codex_cli_path,
    is_codex_cli_authenticated,
    run_codex_login,
)


AUTH_DIR = Path.home() / ".gaia" / "auth"
AUTH_FILE = AUTH_DIR / "profiles.json"
GEMINI_ENV_FILE_NAME = ".env.gemini.local"
GEMINI_ENV_DEFAULT_MODEL = "gemini-2.5-pro"
GEMINI_VERTEX_TOKEN_SENTINEL = "__gaia_vertex_ai__"
GEMINI_VERTEX_ENV_KEYS = (
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GAIA_GEMINI_BACKEND",
)

PROVIDER_ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": "OLLAMA_API_KEY",
}

PROVIDER_LOGIN_URL = {
    "openai": "https://platform.openai.com/settings/organization/api-keys",
    "gemini": "https://aistudio.google.com/app/apikey",
    "ollama": "",
}

@dataclass
class AuthProfile:
    provider: str
    token: str
    source: str
    updated_at: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ensure_auth_dir() -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    try:
        AUTH_DIR.chmod(0o700)
    except OSError:
        pass


def _load_profiles() -> dict[str, dict[str, Any]]:
    if not AUTH_FILE.exists():
        return {}
    try:
        with AUTH_FILE.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        if isinstance(data, dict):
            return data
    except Exception:
        return {}
    return {}


def _save_profiles(payload: dict[str, dict[str, Any]]) -> None:
    _ensure_auth_dir()
    with AUTH_FILE.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)


def _resolve_gemini_env_file() -> Path:
    raw = str(os.getenv("GAIA_GEMINI_ENV_FILE", "") or "").strip()
    if raw:
        return Path(raw).expanduser()
    cwd = Path.cwd()
    for base in (cwd, *cwd.parents):
        candidate = base / GEMINI_ENV_FILE_NAME
        if candidate.exists():
            return candidate
    return cwd / GEMINI_ENV_FILE_NAME


def _parse_env_assignments(text: str) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        assignments[key] = value
    return assignments


def _read_gemini_env_assignments() -> tuple[dict[str, str], Path | None]:
    path = _resolve_gemini_env_file()
    if not path.exists():
        return {}, None
    try:
        assignments = _parse_env_assignments(path.read_text(encoding="utf-8"))
    except Exception:
        return {}, path
    return assignments, path


def _read_gemini_env_token() -> tuple[str | None, Path | None]:
    assignments, path = _read_gemini_env_assignments()
    if path is None:
        return None, None
    token = str(assignments.get("GEMINI_API_KEY") or "").strip()
    if not token:
        return None, path
    return token, path


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _gemini_vertex_source(*, export: bool = False) -> str | None:
    assignments, path = _read_gemini_env_assignments()
    merged = dict(assignments)
    for key in GEMINI_VERTEX_ENV_KEYS:
        env_value = str(os.getenv(key) or "").strip()
        if env_value:
            merged[key] = env_value

    backend = str(merged.get("GAIA_GEMINI_BACKEND") or "").strip().lower()
    vertex_requested = _truthy(merged.get("GOOGLE_GENAI_USE_VERTEXAI")) or backend in {
        "vertex",
        "vertex_ai",
        "vertexai",
    }
    if not vertex_requested:
        return None

    project = str(merged.get("GOOGLE_CLOUD_PROJECT") or "").strip()
    location = str(merged.get("GOOGLE_CLOUD_LOCATION") or "").strip()
    if not project or not location:
        return None

    credentials_path = str(merged.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    if credentials_path:
        expanded = Path(credentials_path).expanduser()
        if not expanded.exists():
            return None
        merged["GOOGLE_APPLICATION_CREDENTIALS"] = str(expanded)
    else:
        adc_path = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
        if not adc_path.exists():
            return None

    if export:
        for key in ("GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "GOOGLE_APPLICATION_CREDENTIALS"):
            value = str(merged.get(key) or "").strip()
            if value and not str(os.getenv(key) or "").strip():
                os.environ[key] = value
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

    if path is not None:
        return f"vertex_ai:{path}"
    return "vertex_ai:env"


def _write_gemini_env_token(token: str) -> Path:
    path = _resolve_gemini_env_file()
    assignments: dict[str, str] = {}
    if path.exists():
        try:
            assignments = _parse_env_assignments(path.read_text(encoding="utf-8"))
        except Exception:
            assignments = {}
    assignments["GEMINI_API_KEY"] = token.strip()
    assignments.setdefault("GAIA_LLM_PROVIDER", "gemini")
    assignments.setdefault("VISION_PROVIDER", "gemini")
    assignments.setdefault("GAIA_LLM_MODEL", GEMINI_ENV_DEFAULT_MODEL)
    assignments.setdefault("VISION_MODEL", assignments.get("GAIA_LLM_MODEL", GEMINI_ENV_DEFAULT_MODEL))
    ordered_keys = [
        "GEMINI_API_KEY",
        "GAIA_LLM_PROVIDER",
        "VISION_PROVIDER",
        "GAIA_LLM_MODEL",
        "VISION_MODEL",
    ]
    seen: set[str] = set()
    lines: list[str] = []
    for key in ordered_keys:
        if key not in assignments:
            continue
        value = assignments[key]
        lines.append(f"{key}={json.dumps(value, ensure_ascii=False)}")
        seen.add(key)
    for key in sorted(assignments):
        if key in seen:
            continue
        value = assignments[key]
        lines.append(f"{key}={json.dumps(value, ensure_ascii=False)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _openid_state_profile(provider: str) -> dict[str, Any] | None:
    return _load_profiles().get(provider)


def _is_oauth_source(source: Any) -> bool:
    return isinstance(source, str) and source.strip().lower().startswith("oauth")


def _save_provider_profile(provider: str, token: str, source: str = "manual", metadata: dict[str, Any] | None = None) -> None:
    payload = _load_profiles()
    payload[provider] = AuthProfile(
        provider=provider,
        token=token,
        source=source,
        updated_at=_now_iso(),
        metadata=metadata or {},
    ).to_dict()
    _save_profiles(payload)


def _remove_legacy_codex_profile() -> bool:
    """Delete token copies created by older GAIA Codex OAuth integration."""

    payload = _load_profiles()
    profile = payload.get("openai")
    if not isinstance(profile, dict) or not _is_oauth_source(profile.get("source")):
        return False
    del payload["openai"]
    _save_profiles(payload)
    return True


def get_stored_token(provider: str) -> str | None:
    profile = _openid_state_profile(provider)
    if not isinstance(profile, dict):
        return None

    token = profile.get("token")
    if not isinstance(token, str) or not token.strip():
        return None

    if provider == "openai" and _is_oauth_source(profile.get("source")):
        return None

    return token.strip()


def get_token_source(provider: str) -> tuple[str | None, str | None]:
    if provider == "gemini":
        vertex_source = _gemini_vertex_source()
        if vertex_source:
            return GEMINI_VERTEX_TOKEN_SENTINEL, vertex_source

    env_key = PROVIDER_ENV_MAP.get(provider, "")
    env_token = os.getenv(env_key, "") if env_key else ""
    if env_token:
        return env_token, f"env:{env_key}"

    if provider == "openai":
        _remove_legacy_codex_profile()
        if is_codex_cli_authenticated():
            return CODEX_OAUTH_TOKEN_SENTINEL, CODEX_AUTH_SOURCE

    if provider == "ollama":
        return "ollama", "local:ollama"

    if provider == "gemini":
        token, path = _read_gemini_env_token()
        if token and path is not None:
            return token, f"envfile:{path}"

    token = get_stored_token(provider)
    if token:
        profile = _openid_state_profile(provider)
        if isinstance(profile, dict):
            source = str(profile.get("source") or "").strip()
            if source:
                return token, source
        return token, "stored"
    return None, None


def delete_token(provider: str) -> bool:
    data = _load_profiles()
    if provider == "all":
        if not data:
            return False
        data.clear()
        _save_profiles(data)
        return True
    if provider not in data:
        return False
    del data[provider]
    _save_profiles(data)
    return True


def mask_token(token: str, show: int = 6) -> str:
    token = token.strip()
    if not token:
        return ""
    if len(token) <= show:
        return "*" * len(token)
    return f"{token[:4]}{'*' * max(4, len(token) - 10)}{token[-4:]}"


def provider_login_url(provider: str) -> str:
    return PROVIDER_LOGIN_URL.get(provider, "")


def _interactive_login_openai(open_browser: bool = True, force_reauth: bool = False) -> str | None:
    _remove_legacy_codex_profile()
    if not force_reauth and is_codex_cli_authenticated():
        print("Codex CLI OAuth 세션을 재사용합니다. 토큰은 GAIA로 복사하지 않습니다.")
        return CODEX_OAUTH_TOKEN_SENTINEL

    if not sys.stdin.isatty():
        return None

    if not codex_cli_path():
        print("Codex CLI가 필요합니다. `npm install -g @openai/codex` 설치 후 다시 시도하세요.")
        return None
    if not open_browser:
        print("Codex CLI 로그인은 자체 브라우저/URL 플로우를 사용합니다.")
    print("OpenAI OAuth를 위해 공식 Codex CLI 로그인(`codex login`)을 시작합니다.")
    if not run_codex_login():
        print("`codex login`이 실패했거나 로그인 상태를 확인하지 못했습니다.")
        return None
    print("OpenAI OAuth(Codex) 인증이 완료되었습니다. 토큰은 Codex가 계속 관리합니다.")
    return CODEX_OAUTH_TOKEN_SENTINEL


def interactive_login(
    provider: str,
    open_browser: bool = True,
    token: str | None = None,
    use_oauth: bool | None = None,
    force_reauth: bool = False,
) -> str | None:
    provider = provider.lower().strip()
    if provider not in PROVIDER_ENV_MAP:
        return None
    if provider == "ollama":
        write_env_if_set(provider, "ollama")
        return "ollama"

    if token and token.strip():
        _save_provider_profile(provider, token.strip(), source="manual")
        if provider == "gemini":
            _write_gemini_env_token(token.strip())
        return token.strip()

    if use_oauth is None:
        use_oauth = provider == "openai"

    if not sys.stdin.isatty():
        return None

    if provider == "openai" and use_oauth:
        return _interactive_login_openai(open_browser=open_browser, force_reauth=force_reauth)

    if open_browser:
        url = provider_login_url(provider)
        if url:
            print(f"브라우저에서 {provider} 인증 페이지를 엽니다: {url}")
            try:
                webbrowser.open(url)
            except Exception:
                print("브라우저 자동 실행을 실패했습니다. 위 주소를 직접 열어주세요.")

    prompt_map = {
        "openai": "OpenAI API 키",
        "gemini": "Gemini API 키",
        "ollama": "Ollama API 키",
    }
    value = getpass.getpass(f"{prompt_map.get(provider, 'API 토큰')} 입력 (빈 값이면 취소): ").strip()
    if not value:
        return None

    _save_provider_profile(provider, value, source="manual")
    if provider == "gemini":
        _write_gemini_env_token(value)
    return value


def resolve_auth(
    provider: str,
    strategy: str = "reuse",
    method: str = "auto",
    *,
    open_browser: bool = True,
) -> tuple[str | None, str | None]:
    provider = provider.lower().strip()
    strategy = strategy.lower().strip()
    method = method.lower().strip()
    if provider not in PROVIDER_ENV_MAP:
        return None, None
    if provider == "ollama":
        write_env_if_set(provider, "ollama")
        return "ollama", "local:ollama"
    if strategy not in {"reuse", "fresh"}:
        strategy = "reuse"
    if method not in {"auto", "oauth", "manual"}:
        method = "auto"

    use_oauth: bool | None = None
    if provider == "openai":
        if method == "oauth":
            use_oauth = True
        elif method == "manual":
            use_oauth = False
        else:
            use_oauth = True

    def _matches_selected_method(
        token_value: str | None,
        source_value: str | None,
        provider_value: str,
        method_value: str,
    ) -> bool:
        if not token_value:
            return False
        if provider_value != "openai" or method_value == "auto":
            return True

        # Environment token source cannot carry explicit metadata.
        # Treat JWT-like tokens as oauth candidates, otherwise manual.
        if source_value and source_value.startswith("env:"):
            if method_value == "oauth":
                return token_value.count(".") == 2
            return True

        profile = _openid_state_profile(provider_value)
        if not isinstance(profile, dict):
            return False
        profile_source = str(profile.get("source", "")).strip().lower()
        if method_value == "oauth":
            return profile_source.startswith("oauth")
        return not profile_source.startswith("oauth")

    if strategy == "fresh":
        token = interactive_login(
            provider=provider,
            open_browser=open_browser,
            use_oauth=use_oauth,
            force_reauth=(provider == "openai" and use_oauth is True),
        )
        if not token:
            return None, None
        write_env_if_set(provider, token)
        profile = _openid_state_profile(provider)
        if isinstance(profile, dict):
            profile_source = str(profile.get("source", "")).strip()
            if profile_source:
                return token, profile_source
        return token, "fresh"

    token, source = get_token_source(provider)
    if token and _matches_selected_method(token, source, provider, method):
        write_env_if_set(provider, token)
        return token, source or "stored"

    token = interactive_login(
        provider=provider,
        open_browser=open_browser,
        use_oauth=use_oauth,
        force_reauth=False,
    )
    if not token:
        return None, None
    write_env_if_set(provider, token)
    profile = _openid_state_profile(provider)
    if isinstance(profile, dict):
        profile_source = str(profile.get("source", "")).strip()
        if profile_source:
            return token, profile_source
    return token, "fresh"


def write_env_if_set(provider: str, token: str | None) -> None:
    env_key = PROVIDER_ENV_MAP.get(provider)
    if not env_key:
        return
    if provider == "gemini" and token == GEMINI_VERTEX_TOKEN_SENTINEL:
        _gemini_vertex_source(export=True)
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
        return
    if provider == "openai" and token == CODEX_OAUTH_TOKEN_SENTINEL:
        os.environ["GAIA_OPENAI_AUTH_SOURCE"] = CODEX_AUTH_SOURCE
        return
    if provider == "ollama" and not token:
        os.environ.setdefault(env_key, "ollama")
        return
    if token:
        os.environ[env_key] = token
    else:
        os.environ.pop(env_key, None)


def list_status() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for provider, env_key in PROVIDER_ENV_MAP.items():
        token, source = get_token_source(provider)
        if token:
            if token == GEMINI_VERTEX_TOKEN_SENTINEL:
                mask = "vertex-ai"
            elif token == CODEX_OAUTH_TOKEN_SENTINEL:
                mask = "codex-session"
            else:
                mask = mask_token(token)
            result[provider] = {
                "status": "configured",
                "mask": mask,
                "source": source or "unknown",
                "env_key": env_key,
            }
        else:
            result[provider] = {
                "status": "not-configured",
                "mask": "",
                "source": "none",
                "env_key": env_key,
            }
    return result


def build_auth_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gaia auth",
        description="GAIA authentication helpers",
    )
    subparsers = parser.add_subparsers(dest="auth_command", required=False)

    login_parser = subparsers.add_parser("login", help="Store provider credentials for GAIA")
    login_parser.add_argument("--provider", choices=tuple(PROVIDER_ENV_MAP.keys()), required=True)
    login_parser.add_argument("--token", help="Token/API key to store directly")
    login_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open provider login page in browser",
    )
    login_parser.add_argument(
        "--method",
        choices=("auto", "oauth", "manual"),
        default="auto",
        help="인증 방식 선택: auto(기본), oauth(브라우저 로그인), manual(API 키 입력)",
    )

    subparsers.add_parser("status", help="Show configured auth providers")

    logout_parser = subparsers.add_parser("logout", help="Clear stored token")
    logout_parser.add_argument("--provider", choices=("openai", "gemini", "ollama", "all"), required=True)

    return parser


def run_auth(argv: list[str] | None = None) -> int:
    parser = build_auth_parser()
    args = parser.parse_args(list(argv or []))

    if args.auth_command == "login":
        provider = str(args.provider)
        use_oauth = None
        if args.method == "oauth":
            use_oauth = True
        elif args.method == "manual":
            use_oauth = False

        token = interactive_login(
            provider=provider,
            open_browser=not args.no_browser,
            token=args.token,
            use_oauth=use_oauth,
            force_reauth=(provider == "openai" and use_oauth is True),
        )
        if not token:
            print("토큰이 입력되지 않아 로그인에 실패했습니다.")
            return 1
        write_env_if_set(provider, token)
        if token == CODEX_OAUTH_TOKEN_SENTINEL:
            print("Codex OAuth 연결을 확인했습니다. GAIA에는 토큰을 저장하지 않았습니다.")
        else:
            print(f"{provider} 인증 정보가 저장되었습니다.")
        return 0

    if args.auth_command == "status":
        for provider, value in list_status().items():
            if value["status"] == "configured":
                print(
                    f"- {provider}: {value['status']} "
                    f"({value['source']}) [{value['mask']}]"
                )
            else:
                print(f"- {provider}: {value['status']}")
        return 0

    if args.auth_command == "logout":
        provider = str(args.provider)
        if delete_token(provider):
            print(f"{provider} 저장 토큰이 삭제되었습니다.")
            return 0
        print(f"{provider} 저장 토큰이 없습니다.")
        return 1

    parser.print_help()
    return 0
