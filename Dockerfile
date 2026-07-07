FROM docker.io/denoland/deno:bin AS deno

FROM docker.io/python:3.13-slim

COPY --from=deno /deno /usr/local/bin/deno

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# writable home for yt-dlp/deno caches when running as a non-root user
ENV HOME=/tmp

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jellyfin-youtube-downloader.py .
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

VOLUME /downloads

ENTRYPOINT ["/entrypoint.sh"]
