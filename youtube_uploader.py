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
import anthropic
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


# A core set of hashtags that fits every cryptid/horror Short on the
# channel. The topic itself is added on top of these as its own hashtag.
BASE_HASHTAGS = [
    "#cryptid", "#paranormal", "#scary", "#horror",
    "#unexplained", "#creepy", "#mystery", "#shorts",
]


def _topic_hashtag(topic: str) -> str:
    """Turns a topic like 'El Chupacabra' into a clean '#ElChupacabra' tag."""
    cleaned = "".join(ch for ch in topic if ch.isalnum() or ch.isspace())
    return "#" + "".join(word.capitalize() for word in cleaned.split())


def generate_seo_metadata(topic: str) -> tuple:
    """
    Uses Claude to write an engaging, clickable YouTube title for the
    topic, then builds an SEO-friendly description packed with relevant
    hashtags. Returns (title, description).

    The title is always forced to end with '#shorts' so YouTube treats the
    video as a Short, and the description leads with the title before the
    hashtag block.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = (
        "You write titles for a horror and cryptozoology YouTube Shorts channel.\n"
        f"The video is about: {topic}\n\n"
        "Write ONE engaging, clickable, scroll-stopping title for this Short.\n\n"
        "Rules:\n"
        "- Make it punchy and curiosity-driving, like a viral Shorts title\n"
        "- Good examples of the style: 'The REAL Chupacabra Story', "
        "'What Lives In The Woods?', 'Nobody Survives Lake Champlain'\n"
        "- It MUST include the topic name or a clear reference to it\n"
        "- Keep it under 70 characters\n"
        "- Title Case or natural casing, you may use ALL CAPS on one key word for emphasis\n"
        "- No quotes, no emojis, no hashtags, no explanation\n"
        "- Respond with ONLY the title text, nothing else\n"
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=40,
            messages=[{"role": "user", "content": prompt}],
        )
        title_core = message.content[0].text.strip().strip('"').strip()
    except Exception:
        # If the API call fails for any reason, fall back to a simple
        # title so the upload still succeeds.
        title_core = f"The REAL {topic.title()} Story"

    if not title_core:
        title_core = f"The REAL {topic.title()} Story"

    # Force the #shorts tag onto the end of the title.
    title = f"{title_core} #shorts"
    # YouTube titles are capped at 100 characters.
    title = title[:100]

    # Build the description: lead with the title, a short hook line, then
    # the hashtag block (topic hashtag first, then the standard set).
    hashtags = [_topic_hashtag(topic)] + [t for t in BASE_HASHTAGS if t != "#shorts"] + ["#shorts"]
    description = (
        f"{title_core}\n\n"
        "Real stories, sightings, and unexplained mysteries from the world "
        "of cryptids and the paranormal. Watch with the lights on.\n\n"
        + " ".join(hashtags)
    )

    return title, description


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