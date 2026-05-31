import os
import requests
import yt_dlp
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

JELLYFIN_URL = os.environ["JELLYFIN_URL"]
JELLYFIN_API_KEY = os.environ["JELLYFIN_API_KEY"]
JELLYFIN_USER_ID = os.environ["JELLYFIN_USER_ID"]

def get_jellyfin_items():
    resp = requests.get(
        f"{JELLYFIN_URL}/Users/{JELLYFIN_USER_ID}/Items",
        headers={"X-Emby-Token": JELLYFIN_API_KEY},
        # TODO: set ISPLAYED to false
        params={
            "IsPlayed": False,
            "MediaTypes": "Video",
            "parentId": "e59b37148e0ff06f0d35b0c3c714e75c",
            "recursive": True,
            "filters": "IsFavorite",
            "fields": "Path",
        },
    )  #
    resp.raise_for_status()
    return resp.json()["Items"]

def download_video(youtube_id, series_name, season_name):
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    opts = {
        "outtmpl": f"./downloaded_videos/{series_name}/{season_name}/%(title)s.%(ext)s",
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
    for item in items:
        print(f"Processing: {item['Name']}")
        youtube_id = Path(item["Path"]).stem
        print(f"Downloading {item['Name']} ({youtube_id})")
        result = download_video(youtube_id, item["SeriesName"], item["SeasonName"])
        if result == True:
            mark_unfavourited(item["Id"])
            print(f"Marked unfavourited: {item['Name']}")
        else:
            print(f"Download failed, skipping unfavourite: {item['Name']}")


if __name__ == "__main__":
    main()
