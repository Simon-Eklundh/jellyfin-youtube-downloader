import os
import requests
import yt_dlp
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.environ["JELLYFIN_URL"]
JELLYFIN_API_KEY = os.environ["JELLYFIN_API_KEY"]
JELLYFIN_USER_ID = os.environ["JELLYFIN_USER_ID"]
YOUTUBE_LIBRARY_ID = os.environ["YOUTUBE_LIBRARY_ID"]

def get_jellyfin_items():
    resp = requests.get(
        f"{JELLYFIN_URL}/Users/{JELLYFIN_USER_ID}/Items",
        headers={"X-Emby-Token": JELLYFIN_API_KEY},
        # TODO: set ISPLAYED to false
        params={
            "IsPlayed": True,
            "MediaTypes": "Video",
            "parentId": YOUTUBE_LIBRARY_ID,
            "recursive": True,
            "filters": "IsFavorite",
            "fields": "Path",
        },
    )  #
    resp.raise_for_status()
    return resp.json()["Items"]

def ensure_channel_images(youtube_id, series_name, season_name):
    channel_dir = Path(f"/downloads/{series_name}")
    season_dir = channel_dir / season_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    season_dir.mkdir(parents=True, exist_ok=True)

    if (channel_dir / "cover.jpg").exists():
        return

    print(f"Downloading channel images for {series_name}")

    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={youtube_id}", download=False)

    channel_url = info.get("channel_url") or info.get("uploader_url")
    if not channel_url:
        return

    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
        channel_info = ydl.extract_info(channel_url, download=False)

    thumbnails = channel_info.get("thumbnails", [])
    if not thumbnails:
        return

    by_id = {t["id"]: t["url"] for t in thumbnails if "id" in t and "url" in t}

    cover_url = by_id.get("avatar_uncropped")
    backdrop_url = by_id.get("banner_uncropped")

    if cover_url:
        img = requests.get(cover_url).content
        (channel_dir / "cover.jpg").write_bytes(img)
        (season_dir / "cover.jpg").write_bytes(img)
    if backdrop_url:
        img = requests.get(backdrop_url).content
        (channel_dir / "backdrop.jpg").write_bytes(img)


def download_video(youtube_id, series_name, season_name):
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    opts = {
        "outtmpl": f"/downloads/{series_name}/{season_name}/%(title)s.%(ext)s",
        "embedthumbnail": True,
        "embedmetadata": True,
        "writesubtitles": True,
        "merge_output_format": "mkv",
        "sponsorblock_remove": ["sponsor", "selfpromo", "interaction"],
        "subtitleslangs": ["en"],
        "embedsubs": True,
    }
    TRANSIENT_ERRORS = ["429", "too many requests", "rate limit", "503", "502", "sign in to confirm"]
    PERMANENT_ERRORS = ["video unavailable", "has been removed", "private video", "does not exist", "copyright"]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return True
    except yt_dlp.utils.DownloadError as e:
        msg = str(e).lower()
        if any(x in msg for x in TRANSIENT_ERRORS):
            print(f"Transient error, try again later: {e}")
            return False
        if any(x in msg for x in PERMANENT_ERRORS):
            print(f"Video permanently unavailable, skipping: {e}")
            return True
        print(f"Unknown yt-dlp error: {e}")
        return False


def mark_unfavourited(item_id):
    # TODO: change this to work properly
    resp = requests.post(
        f"{JELLYFIN_URL}/UserItems/{item_id}/UserData",
        headers={"X-Emby-Token": JELLYFIN_API_KEY},
        json={"IsFavorite": False},
        params={"userId": JELLYFIN_USER_ID},
    )
    resp.raise_for_status()


def main():
    items = get_jellyfin_items()
    print(f"Found {len(items)} items to process.")
    seen_channels = set()
    for item in items:
        print(f"Processing: {item['Name']}")
        youtube_id = Path(item["Path"]).stem
        series_name = item["SeriesName"]
        season_name = item["SeasonName"]
        if series_name not in seen_channels:
            ensure_channel_images(youtube_id, series_name, season_name)
            seen_channels.add(series_name)
        print(f"Downloading {item['Name']} ({youtube_id})")
        result = download_video(youtube_id, series_name, season_name)
        if result == True:
            mark_unfavourited(item["Id"])
            print(f"Marked unfavourited: {item['Name']}")
        else:
            print(f"Download failed, skipping unfavourite: {item['Name']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
