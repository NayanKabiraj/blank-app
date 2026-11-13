# Saved Shorts

When the YouTube secrets are not set (or on a dry run), the daily workflow saves each
day's videos here as `videos/<date>/en.mp4` and `hi.mp4`, with the title, description
and tags in `<lang>_youtube.txt`, so you can upload them by hand.

Once `YT_CLIENT_ID`, `YT_CLIENT_SECRET` and `YT_REFRESH_TOKEN` are added, videos are
uploaded to YouTube instead and nothing new is saved here.
