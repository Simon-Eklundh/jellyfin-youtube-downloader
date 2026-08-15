# jellyfin-youtube-downloader
a jellyfin-based youtube downloader for tubearchivist users


## Requirements:

1. a jellyfin server
2. youtube videos on the server with their youtube id in the path (tubearchivist does this by default)

## Why should I run this?

This is a simple backup solution for people who (like me) use tubearchivist to download youtube videos, but want most of them deleted after watch.

## How does it work?

It calls jellyfin asking for watched and favourited videos in a set library. It then downloads the video from youtube (with sponsorblock), and unfavourites it in jellyfin so it can be deleted

Optionally, for age restricted content, you can add a cookie file.

Optionally, you can also get notified of run results via [Apprise](https://github.com/caronc/apprise-api).

By default the YouTube video ID is taken to be the whole filename (e.g. tubearchivist's default naming). If your filenames embed the ID differently (e.g. `title [VIDEO_ID].mp4`), set `YOUTUBE_ID_REGEX` to a regex with a capture group around the ID, such as `\[([^\]]+)\]`. Run `python jellyfin-youtube-downloader.py --dry-run` to check the regex against one real item (prints the path, filename stem, and what ID would be extracted) without downloading or notifying anything.

## docker compose

```docker-compose
services:
  jellyfin-youtube-downloader:
    image: simoneklundh/jellyfin-youtube-backuper
    # run as a non-root user; the media path and cookie file must be
    # writable by this UID:GID (65534 is "nobody")
    user: "65534:65534"
    environment:
      - JELLYFIN_URL=
      - JELLYFIN_API_KEY=
      - JELLYFIN_USER_ID=
      - YOUTUBE_LIBRARY_ID=
      - COOKIES_FILE=somePathHere.txt
      - APPRISE_URL=http://your-apprise-api-host:8000
      - VERBOSE_FAIL_NOTIFICATIONS=false
      - YOUTUBE_ID_REGEX=
    volumes:
      - /your/media/path:/downloads
      - /your/path/to/cookieFile/cookiesFile.txt:/somepathhere/somepathHere.txt
```
