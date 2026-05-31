#!/bin/sh
printenv > /etc/environment
python /app/jellyfin-youtube-downloader.py
cron -f &
CRON_PID=$!
trap "kill $CRON_PID" INT TERM
wait $CRON_PID
