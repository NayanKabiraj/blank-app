# Google / YouTube sign-in from a phone

The project has ONE sign-in implementation, `shorts/ytauth.py`. No terminal and no localhost are needed.

**Flow**: an upload needs YouTube → `ytauth.credentials()` refreshes an expired access token silently → only on `invalid_grant` it writes a
pending authorization (`data/oauth_pending.json`) and Claude shows the 🔐 message (`python -m shorts.ytauth banner`) → you tap the link,
sign in, tap **Allow** → Google redirects to `https://nayankabiraj.github.io/blank-app/oauth/callback.html` (GitHub Pages, `docs/oauth/callback.html`)
→ it opens a GitHub "oauth-callback" issue form for you (tap **Submit new issue**) → `.github/workflows/oauth-callback.yml` (owner-only) checks state,
expiry and PKCE, exchanges the code, stores the new refresh token encrypted in `data/yt_token_en.enc`, redacts/closes the issue and uploads what
waits in `videos/unpublished/` (the checkpoint - nothing is rendered again).

**Error classes** (`ytauth.classify`): `invalid_grant` → authorize; expired access token → silent refresh; `quotaExceeded`/`uploadLimitExceeded` →
report, no re-authorization; `rateLimitExceeded`/429, 5xx, timeouts → retry with back-off; `insufficientPermissions` → configuration problem, no loop.

**One-time Google Cloud / GitHub setup**
1. Google Auth Platform → Clients → your Web client → Authorized redirect URIs: add `https://nayankabiraj.github.io/blank-app/oauth/callback.html`.
2. GitHub repo → Settings → Pages → Source "Deploy from a branch", branch `main`, folder `/docs`.
3. (Testing mode) the refresh token still expires after ~7 days; the flow above renews it in one tap. Publishing the app ("In production") removes the expiry.
4. Enable the YouTube Data API and YouTube Analytics API (already done).

Security: OAuth Authorization Code + PKCE (S256) + `state` + expiry (24 h, `OAUTH_PENDING_TTL_MIN`); only issues opened by the repository owner are trusted; the
code is single-use and useless without the PKCE verifier (stored encrypted with a key derived from the client secret) and the client secret; no token or secret is printed.
