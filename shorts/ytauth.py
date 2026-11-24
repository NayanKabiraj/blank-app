"""The ONE Google/YouTube sign-in of this project, built for a phone: no terminal, no localhost.

How it works (details: docs/oauth-mobile.md)

* Every upload asks `credentials()` for a working access token. An expired access token is refreshed silently. Only when
  Google answers `invalid_grant` (the refresh token expired or was revoked - normal after ~7 days while the Google app is in
  "Testing") does `request_authorization()` create ONE pending authorization (data/oauth_pending.json, public-safe: state, PKCE
  challenge, expiry, the interrupted operation, the PKCE verifier encrypted with a key derived from the client secret) and
  `banner()` formats the message that Claude shows in the chat.
* The owner taps the link, signs in, taps Allow. Google redirects to the public HTTPS page docs/oauth/callback.html (GitHub
  Pages), which forwards the result to a GitHub "oauth-callback" issue; the workflow oauth-callback.yml runs `callback-issue`
  (state + expiry + owner checks, PKCE code exchange, token verified and stored encrypted in data/yt_token_en.enc), redacts and
  closes the issue, and uploads what waits in videos/unpublished/ (that queue is the checkpoint: nothing is re-rendered).
* Nothing secret is ever printed or committed in the clear. Google's password and consent screen are never automated.

    python -m shorts.ytauth banner     # the chat message for a pending authorization ("" if none) - what Claude shows
    python -m shorts.ytauth url        # create (or reuse) a pending authorization and print the banner
    python -m shorts.ytauth status     # pending / restored / not needed
    python -m shorts.ytauth check      # does the stored sign-in refresh?
    python -m shorts.ytauth exchange <callback-address-or-code>   # fallback: finish by hand with what the callback page shows
    python -m shorts.ytauth callback-issue                        # (workflow) finish from the issue text in $ISSUE_BODY
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sys
import urllib.parse

import requests

from . import config

log = logging.getLogger("shorts.ytauth")

TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPE = " ".join(["https://www.googleapis.com/auth/youtube.upload",             # uploads + thumbnails
                  "https://www.googleapis.com/auth/youtube.readonly",          # the channel check (shorts/channel_trends.py)
                  "https://www.googleapis.com/auth/yt-analytics.readonly"])
REQUIRED_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
PENDING = config.DATA_DIR / "oauth_pending.json"
STATUS = config.DATA_DIR / "oauth_status.json"
TTL_MIN = int(os.getenv("OAUTH_PENDING_TTL_MIN", "1440"))                       # how long an outstanding request stays valid (24 h)


class AuthRequired(Exception):
    """Google needs the owner to authorize again (refresh token expired/revoked, or no token stored)."""


# ------------------------------------------------------------------------------------------ error classification
def _http(exc) -> tuple[int, set[str]]:
    status = getattr(getattr(exc, "resp", None), "status", 0) or getattr(exc, "status_code", 0) or 0
    reasons: set[str] = set()
    try:
        payload = json.loads(exc.content.decode() if isinstance(exc.content, bytes) else exc.content)
        err = payload.get("error", {})
        reasons |= {e.get("reason", "") for e in err.get("errors", []) if isinstance(e, dict)}
        reasons.add(str(err.get("status", "")))
    except Exception:  # noqa: BLE001
        pass
    return int(status or 0), reasons


def classify(exc: BaseException) -> str:
    """auth (invalid_grant) | quota | rate | scope | retry | other. Only `auth` ever asks the owner to authorize again."""
    if isinstance(exc, AuthRequired):
        return "auth"
    text = str(exc)
    status, reasons = _http(exc)
    low = text.lower()
    if "invalid_grant" in low or "token has been expired or revoked" in low:
        return "auth"
    if reasons & {"quotaExceeded", "dailyLimitExceeded", "uploadLimitExceeded"} or "exceeded the number of videos" in low:
        return "quota"
    if reasons & {"rateLimitExceeded", "userRateLimitExceeded"} or status == 429:
        return "rate"
    if reasons & {"insufficientPermissions", "ACCESS_TOKEN_SCOPE_INSUFFICIENT"} or "insufficient authentication scopes" in low \
            or "insufficientpermissions" in low or "access_token_scope_insufficient" in low:
        return "scope"
    if status in (401,) or "authError" in reasons:
        return "auth"
    if status >= 500 or isinstance(exc, (TimeoutError, ConnectionError, OSError)) or type(exc).__name__ in (
            "TransportError", "Timeout", "ReadTimeout", "ConnectTimeout", "ConnectionError", "SSLError", "ChunkedEncodingError"):
        return "retry"
    return "other"


# -------------------------------------------------------------------------------------------------- token storage
def _fernet():
    from cryptography.fernet import Fernet
    key = base64.urlsafe_b64encode(hashlib.sha256(("yt-token:" + config.YT_CLIENT_SECRET).encode()).digest())
    return Fernet(key)


def token_file(lang: str):
    return config.DATA_DIR / f"yt_token_{lang}.enc"


def load_saved_token(lang: str) -> str:
    """The refresh token the callback saved (encrypted in data/), or '' (also '' when the client secret changed)."""
    for name in (lang, "en"):
        f = token_file(name)
        if f.exists() and config.YT_CLIENT_SECRET:
            try:
                return _fernet().decrypt(f.read_bytes()).decode()
            except Exception:  # noqa: BLE001
                return ""
    return ""


def candidates(lang: str = "en") -> list[str]:
    """Refresh tokens to try, newest source first: the one the phone flow stored, then the YT_REFRESH_TOKEN secret."""
    out = []
    for tok in (load_saved_token(lang), config.YT_REFRESH_TOKENS.get(lang, "")):
        if tok and tok not in out:
            out.append(tok)
    return out


def credentials(lang: str = "en", scopes=None):
    """Google credentials with a fresh access token. Expired access token + valid refresh token -> refreshed silently.
    Raises AuthRequired on invalid_grant (every stored refresh token is dead); network/5xx errors propagate for the caller to retry."""
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    toks = candidates(lang)
    if not toks:
        raise AuthRequired("No Google refresh token is stored.")
    for tok in toks:
        creds = Credentials(None, refresh_token=tok, token_uri=TOKEN_URI, client_id=config.YT_CLIENT_ID,
                            client_secret=config.YT_CLIENT_SECRET, scopes=scopes)
        try:
            creds.refresh(Request())
            return creds
        except RefreshError as e:
            if classify(e) != "auth":
                raise
            log.warning("A stored refresh token was rejected by Google (invalid_grant)")
    raise AuthRequired("Refresh token expired or was revoked (invalid_grant).")


# ------------------------------------------------------------------------------------------- pending authorization
def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _iso(t: dt.datetime) -> str:
    return t.isoformat(timespec="seconds")


def load_pending() -> dict | None:
    try:
        return json.loads(PENDING.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _live(rec: dict | None) -> bool:
    return bool(rec and rec.get("status") == "waiting" and dt.datetime.fromisoformat(rec["expires_at"]) > _now()
                and rec.get("redirect_uri") == config.OAUTH_REDIRECT_URI)


def _queued() -> list[str]:
    try:
        from . import pending
        return [p.name for p in pending.pending()]
    except Exception:  # noqa: BLE001
        return []


def request_authorization(reason: str, kind: str = "youtube_upload") -> dict:
    """Create (or reuse the still-valid) pending authorization and return it. Writes data/oauth_pending.json."""
    rec = load_pending()
    if _live(rec):
        rec["operation"]["queued"] = _queued() or rec["operation"].get("queued", [])
        PENDING.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        return rec
    verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    q = urllib.parse.urlencode({"client_id": config.YT_CLIENT_ID, "redirect_uri": config.OAUTH_REDIRECT_URI, "response_type": "code",
                                "scope": SCOPE, "access_type": "offline", "prompt": "consent", "include_granted_scopes": "true",
                                "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
    rec = {"status": "waiting", "state": state, "created_at": _iso(_now()), "expires_at": _iso(_now() + dt.timedelta(minutes=TTL_MIN)),
           "redirect_uri": config.OAUTH_REDIRECT_URI, "reason": reason[:200], "auth_url": AUTH_URI + "?" + q,
           "verifier_enc": _fernet().encrypt(verifier.encode()).decode(),
           "operation": {"kind": kind, "queued": _queued(), "resume": "python -m shorts.pending flush"}}
    config.DATA_DIR.mkdir(exist_ok=True)
    PENDING.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    log.warning("Google authorization required: %s", reason)
    return rec


def banner(rec: dict | None = None) -> str:
    """The chat message for a pending authorization ('' when none is waiting)."""
    rec = rec or load_pending()
    if not _live(rec):
        return ""
    reason = "Refresh token expired or was revoked." if "invalid_grant" in rec["reason"] or "expired" in rec["reason"].lower() else rec["reason"]
    queued = rec.get("operation", {}).get("queued", [])
    return ("🔐 Google authorization required\n"
            f"Reason: {reason}\n"
            "Action: Tap the authorization link below.\n\n"
            "Tap here to authorize YTConnect\n"
            f"{rec['auth_url']}\n\n"
            f"Status: Waiting for authorization (valid until {rec['expires_at'].replace('+00:00', ' UTC')}).\n"
            + (f"Waiting to resume: {', '.join(queued)}\n" if queued else "")
            + "After authorization, return to this Claude session. The automation will continue automatically where possible.")


def announce(rec: dict) -> None:
    """Log the banner and add it to the workflow run summary (GitHub masks the client id in logs; the link in
    data/oauth_pending.json, which Claude shows in the chat, is the reliable copy)."""
    text = banner(rec)
    print("\n" + text + "\n")
    summ = os.getenv("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a", encoding="utf-8") as f:
            f.write("### 🔐 Google authorization required\n\nAsk Claude to show the authorization link "
                    "(`python -m shorts.ytauth banner` on `main`), tap it, sign in and tap Allow.\n")


def _write_status(status: str, detail: str = "") -> None:
    config.DATA_DIR.mkdir(exist_ok=True)
    STATUS.write_text(json.dumps({"status": status, "at": _iso(_now()), "detail": detail[:200]}, indent=1) + "\n", encoding="utf-8")


def complete(code: str, state: str) -> tuple[bool, str]:
    """Finish a pending authorization. Returns (ok, message); the message never contains a secret."""
    rec = load_pending()
    if not rec or rec.get("status") != "waiting":
        return False, "No authorization is waiting (it may already be done)."
    if not hmac.compare_digest(str(state or ""), rec["state"]):
        return False, "The state does not match the pending authorization - ignored."
    if dt.datetime.fromisoformat(rec["expires_at"]) <= _now():
        _write_status("expired", "authorization request expired")
        return False, "This authorization request has expired; a new link is needed."
    verifier = _fernet().decrypt(rec["verifier_enc"].encode()).decode()
    r = requests.post(TOKEN_URI, data={"code": code, "client_id": config.YT_CLIENT_ID, "client_secret": config.YT_CLIENT_SECRET,
                                       "redirect_uri": rec["redirect_uri"], "grant_type": "authorization_code",
                                       "code_verifier": verifier}, timeout=30)
    body = r.json() if r.content else {}
    if r.status_code != 200:
        return False, f"Google refused the code: {body.get('error')} - {body.get('error_description', '')}"[:200]
    granted = body.get("scope", "")
    if REQUIRED_SCOPE not in granted.split():
        _write_status("scope_missing", "the upload permission was not granted")
        return False, "The YouTube upload permission was not granted (a box was unticked on Google's consent screen). Authorize again and keep every box ticked."
    new = body.get("refresh_token")
    if not new:                                   # Google sometimes returns only an access token: keep the stored one if it still works
        try:
            credentials("en")
            _write_status("restored", "kept the existing refresh token")
            PENDING.unlink(missing_ok=True)
            return True, "Authorization successful; the existing refresh token is still valid and was kept."
        except Exception:  # noqa: BLE001
            return False, "Google returned no refresh token and the stored one no longer works - authorize again."
    chk = requests.post(TOKEN_URI, data={"client_id": config.YT_CLIENT_ID, "client_secret": config.YT_CLIENT_SECRET,
                                         "refresh_token": new, "grant_type": "refresh_token"}, timeout=30)
    if chk.status_code != 200:
        return False, f"The new refresh token did not work: {chk.json().get('error')}"
    config.DATA_DIR.mkdir(exist_ok=True)
    token_file("en").write_bytes(_fernet().encrypt(new.encode()))
    _write_status("restored", "new refresh token stored")
    PENDING.unlink(missing_ok=True)
    return True, f"New credentials have been stored securely (scope: {granted})."


def _parse_callback(text: str) -> tuple[str, str]:
    """(code, state) from a JSON blob {"code","state"}, a callback address, or a bare query string."""
    text = (text or "").strip()
    m = re.search(r"\{.*?\}", text, re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            return str(d.get("code", "")), str(d.get("state", ""))
        except Exception:  # noqa: BLE001
            pass
    q = urllib.parse.parse_qs(urllib.parse.urlparse(text).query if "?" in text else text)
    return (q.get("code", [""])[0], q.get("state", [""])[0])


def _check() -> int:
    try:
        credentials("en")
        print("OK: the stored Google sign-in refreshes.")
        return 0
    except AuthRequired as e:
        print("Authorization needed:", e)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"Could not check ({classify(e)}):", str(e)[:160])
        return 2


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "banner":
        b = banner()
        print(b)
        return 0 if b else 3
    if not (config.YT_CLIENT_ID and config.YT_CLIENT_SECRET):
        print("YT_CLIENT_ID / YT_CLIENT_SECRET are not set.")
        return 1
    if cmd == "url":
        print(banner(request_authorization("Google authorization was requested by hand.")))
        return 0
    if cmd == "status":
        rec = load_pending()
        st = json.loads(STATUS.read_text(encoding="utf-8")) if STATUS.exists() else {}
        print(json.dumps({"pending": bool(_live(rec)), "last": st}))
        return 0
    if cmd == "check":
        return _check()
    if cmd in ("exchange", "callback-issue"):
        text = os.getenv("ISSUE_BODY", "") if cmd == "callback-issue" else " ".join(sys.argv[2:])
        code, state = _parse_callback(text)
        if not code:
            print("No authorization code found.")
            return 1
        ok, msg = complete(code, state)
        print(("✅ Google authorization successful\n" if ok else "❌ Google authorization failed\n") + msg)
        if ok:
            print("Resuming YouTube workflow...")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
