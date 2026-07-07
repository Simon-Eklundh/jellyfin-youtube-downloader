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
    volumes:
      - /your/media/path:/downloads
      - /your/path/to/cookieFile/cookiesFile.txt:/somepathhere/somepathHere.txt
```
