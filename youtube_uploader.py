"""
YOUTUBE UPLOADER
-----------------
What this file does, in plain English:
    Uploads a finished video to your YouTube channel as a Short.

How it fits in the pipeline:
    This is the new STEP 5, used once you've reviewed/approved a video
    that make_reel.py already produced. It does NOT generate video -
    it just publishes an existing finished .mp4 file to YouTube.

What you need for this to work:
    A Google Cloud project with the YouTube Data API enabled, and a
    Client ID saved in your .env file as YOUTUBE_CLIENT_ID.

The first time you run this, a browser window will pop up asking you
to log into Google and approve "Reel Pipeline" accessing your YouTube
channel. This is a one-time step - after that, your approval gets
saved locally so future uploads don't need you to click through it
again.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# This scope specifically grants permission to upload videos only -
# not to read existing videos, delete anything, or manage comments.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

TOKEN_FILE = "youtube_token.pickle"


def _get_authenticated_service():
    """
    Handles the OAuth login flow and returns an authenticated YouTube
    API client, ready to make upload requests.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
                    "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_short(video_path: str, title: str, description: str = "", privacy: str = "private") -> str:
    """
    Uploads a finished video file to YouTube as a Short.
    """
    youtube = _get_authenticated_service()

    if "#shorts" not in title.lower() and "#shorts" not in description.lower():
        description = f"{description}\n\n#Shorts".strip()

    request_body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "categoryId": "24",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media,
    )

    print("      Uploading to YouTube...")
    response = request.execute()

    video_id = response["id"]
    video_url = f"https://youtube.com/shorts/{video_id}"
    return video_url


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("This will run the one-time YouTube authorization flow.")
    print("A browser window should open - log in and click Allow.\n")

    service = _get_authenticated_service()
    print("Successfully authenticated with YouTube!")
    print(f"Token saved to {TOKEN_FILE} for future use.")