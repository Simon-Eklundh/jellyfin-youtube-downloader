#!/bin/sh
trap 'exit 0' INT TERM

python /app/jellyfin-youtube-downloader.py

while true; do
    # sleep until the next 23:00, then run again
    now=$(date +%s)
    next=$(date -d "23:00" +%s)
    if [ "$next" -le "$now" ]; then
        next=$(date -d "tomorrow 23:00" +%s)
    fi
    sleep $((next - now)) &
    wait $!
    python /app/jellyfin-youtube-downloader.py
done
