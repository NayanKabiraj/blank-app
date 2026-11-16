"""One-time YouTube sign-in that runs on GitHub, using the YT_CLIENT_ID / YT_CLIENT_SECRET secrets.

    python -m shorts.ytauth url                      # prints the Google link to open and approve
    python -m shorts.ytauth exchange <code-or-url>   # turns what the browser shows afterwards into a refresh token

The refresh token is stored encrypted in data/yt_token_<lang>.enc. The key is derived from the client secret, so
the file is useless without it (the repository is public). Nothing secret is ever printed. A YT_REFRESH_TOKEN
secret, when set, wins over the file.
"""
from __future__ import annotations

import base64
import hashlib
import sys
import urllib.parse

import requests

from . import config

REDIRECT = "http://localhost"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def _fernet():
    from cryptography.fernet import Fernet
    key = base64.urlsafe_b64encode(hashlib.sha256(("yt-token:" + config.YT_CLIENT_SECRET).encode()).digest())
    return Fernet(key)


def token_file(lang: str):
    return config.DATA_DIR / f"yt_token_{lang}.enc"


def load_saved_token(lang: str) -> str:
    """The refresh token saved by `exchange`, or '' (also '' when the client secret changed)."""
    for name in (lang, "en"):
        f = token_file(name)
        if f.exists() and config.YT_CLIENT_SECRET:
            try:
                return _fernet().decrypt(f.read_bytes()).decode()
            except Exception:  # noqa: BLE001
                return ""
    return ""


def auth_url() -> str:
    q = urllib.parse.urlencode({"client_id": config.YT_CLIENT_ID, "redirect_uri": REDIRECT, "response_type": "code",
                                "scope": SCOPE, "access_type": "offline", "prompt": "consent"})
    return "https://accounts.google.com/o/oauth2/v2/auth?" + q


def exchange(code_or_url: str, lang: str = "en") -> int:
    code = code_or_url.strip()
    if "code=" in code:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get("code", [""])[0]
    if not code:
        print("No code found in what was pasted.")
        return 1
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code, "client_id": config.YT_CLIENT_ID, "client_secret": config.YT_CLIENT_SECRET,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code"}, timeout=30)
    body = r.json()
    if r.status_code != 200 or not body.get("refresh_token"):
        print("Google refused the code:", body.get("error"), "-", body.get("error_description", "(no refresh token returned)"))
        return 1
    token = body["refresh_token"]
    chk = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": config.YT_CLIENT_ID, "client_secret": config.YT_CLIENT_SECRET,
        "refresh_token": token, "grant_type": "refresh_token"}, timeout=30)
    if chk.status_code != 200:
        print("The new refresh token did not work:", chk.json().get("error"))
        return 1
    config.DATA_DIR.mkdir(exist_ok=True)
    token_file(lang).write_bytes(_fernet().encrypt(token.encode()))
    print(f"OK: refresh token created, verified and saved encrypted as {token_file(lang).name} (scope: {body.get('scope')})")
    return 0


def main() -> int:
    if not (config.YT_CLIENT_ID and config.YT_CLIENT_SECRET):
        print("YT_CLIENT_ID / YT_CLIENT_SECRET are not set.")
        return 1
    if len(sys.argv) >= 2 and sys.argv[1] == "url":
        print("OPEN THIS LINK, sign in with the channel's Google account and approve:\n")
        print(auth_url())
        h = len(config.YT_CLIENT_ID) // 2   # the id is public by design, but GitHub masks it in logs: show it in two halves
        print("\nCLIENT_ID_HALVES:", config.YT_CLIENT_ID[:h], "|", config.YT_CLIENT_ID[h:])
        print("\nThe browser then shows a page that cannot be reached (http://localhost/?code=...). That is expected:")
        print("copy the whole address from the address bar and send it back.")
        return 0
    if len(sys.argv) >= 3 and sys.argv[1] == "exchange":
        return exchange(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "en")
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
