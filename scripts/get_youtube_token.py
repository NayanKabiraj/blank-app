"""Run ONCE on your own computer to get a YouTube refresh token for GitHub secrets.

    pip install google-auth-oauthlib
    python scripts/get_youtube_token.py path/to/client_secret.json

A browser window opens; sign in with the Google account that owns the channel (pick the
brand channel if asked). Copy the printed refresh token into the GitHub secret
YT_REFRESH_TOKEN (or YT_REFRESH_TOKEN_HI for a separate Hindi channel).
"""
import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if len(sys.argv) != 2:
    sys.exit(__doc__)
flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
info = json.load(open(sys.argv[1]))
client = info.get("installed") or info.get("web")
print("\nAdd these as GitHub repository secrets:\n")
print("YT_CLIENT_ID     =", client["client_id"])
print("YT_CLIENT_SECRET =", client["client_secret"])
print("YT_REFRESH_TOKEN =", creds.refresh_token)
