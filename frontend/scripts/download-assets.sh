#!/usr/bin/env sh
set -eu
ASSET_URL="${INSIGHTX_ASSETS_URL:-https://d2ol7oe51mr4n9.cloudfront.net/user_3JUUTOGm7ErFIDs70CqGzr2G9Ye/1d0a418f-27a4-4327-a76f-835990b9530d.zip}"
TMP_ARCHIVE="$(mktemp)"
trap 'rm -f "$TMP_ARCHIVE"' EXIT
curl -fsSL "$ASSET_URL" -o "$TMP_ARCHIVE"
unzip -oq "$TMP_ARCHIVE" -d .
test -s public/assets/world/scene-01.mp4
