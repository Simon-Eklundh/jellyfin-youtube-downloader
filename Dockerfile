FROM docker.io/denoland/deno:bin AS deno

FROM docker.io/python:3.13-slim

COPY --from=deno /deno /usr/local/bin/deno

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jellyfin-youtube-downloader.py .
COPY crontab /etc/cron.d/downloader
COPY entrypoint.sh /entrypoint.sh

RUN chmod 0644 /etc/cron.d/downloader && chmod +x /entrypoint.sh

VOLUME /downloads

ENTRYPOINT ["/entrypoint.sh"]
