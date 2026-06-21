"""
REAL IMAGE FINDER (Openverse)
--------------------------------
What this file does, in plain English:
    Searches Openverse - a search engine for openly-licensed media that
    indexes Wikimedia Commons, Flickr, and other open archives - for
    real photos relevant to a topic. This replaces our earlier direct
    Wikimedia approach, which kept hitting an unresolvable rate limit.

How it fits in the pipeline:
    Same role as before - runs alongside clip_finder.py (Pexels). Try
    real photos first; if none exist, fall back to folklore art; fall
    back to Pexels mood footage only if neither turns up anything.

What you need for this to work:
    Nothing to set up by hand! This registers itself with Openverse
    automatically on first use (instant, no approval needed) and saves
    credentials locally.
"""

import os
import json
import time
import requests

OPENVERSE_BASE = "https://api.openverse.org/v1"
CREDENTIALS_FILE = "openverse_credentials.json"

REQUEST_HEADERS = {
    "User-Agent": "ReelPipeline/1.0 (personal project; contact: not-provided)"
}

SKIP_EXTENSIONS = (".svg", ".gif")


def _register_application() -> dict:
    """
    Registers this pipeline as an Openverse application, one time only.
    """
    response = requests.post(
        f"{OPENVERSE_BASE}/auth_tokens/register/",
        json={
            "name": f"ReelPipeline-{int(time.time())}",
            "description": "Personal project: finds real/historical photos for short-form video backgrounds",
            "email": "not-provided@example.com",
        },
        headers=REQUEST_HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    credentials = {
        "client_id": data["client_id"],
        "client_secret": data["client_secret"],
    }

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)

    return credentials


def _get_credentials() -> dict:
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)

    print("      [debug] First time using Openverse - registering automatically...")
    return _register_application()


def _get_access_token() -> str:
    credentials = _get_credentials()

    response = requests.post(
        f"{OPENVERSE_BASE}/auth_tokens/token/",
        data={
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "grant_type": "client_credentials",
        },
        headers=REQUEST_HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _search_openverse(query: str, count: int) -> list:
    token = _get_access_token()
    headers = {**REQUEST_HEADERS, "Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{OPENVERSE_BASE}/images/",
        params={
            "q": query,
            "page_size": count * 2,
            "license_type": "all-cc",
        },
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])
    print(f"      [debug] Openverse returned {len(results)} result(s) for '{query}'")

    urls = []
    for item in results:
        url = item.get("url", "")
        if any(url.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
            continue
        if item.get("width") and item["width"] < 400:
            continue
        urls.append(url)
        if len(urls) >= count:
            break

    return urls


def find_real_images(topic: str, count: int = 4, save_folder: str = "temp/real_images") -> list:
    os.makedirs(save_folder, exist_ok=True)
    urls = _search_openverse(topic, count)
    return _download_images(urls, save_folder)


def find_folklore_art(subject: str, count: int = 4, save_folder: str = "temp/real_images") -> list:
    os.makedirs(save_folder, exist_ok=True)

    search_variants = [
        f"{subject} illustration",
        f"{subject} artwork",
        f"{subject} drawing",
    ]

    for variant in search_variants:
        urls = _search_openverse(variant, count)
        if urls:
            return _download_images(urls, save_folder)

    return []


def _download_images(urls: list, save_folder: str) -> list:
    downloaded_paths = []
    for i, url in enumerate(urls):
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
            response.raise_for_status()
            ext = os.path.splitext(url)[1].split("?")[0] or ".jpg"
            if len(ext) > 5:
                ext = ".jpg"
            file_path = os.path.join(save_folder, f"real_{i}{ext}")
            with open(file_path, "wb") as f:
                f.write(response.content)
            downloaded_paths.append(file_path)
        except Exception as e:
            print(f"      [debug] FAILED to download {url}\n               reason: {e}")

    return downloaded_paths


if __name__ == "__main__":
    print("Testing real photo search: 'Apollo 11 moon landing'")
    real = find_real_images("Apollo 11 moon landing", count=3)
    print(f"Found {len(real)} real images:")
    for p in real:
        print(f"  - {p}")

    print("\nTesting folklore art fallback: 'Bigfoot'")
    art = find_folklore_art("Bigfoot", count=3, save_folder="temp/real_images_test2")
    print(f"Found {len(art)} folklore art images:")
    for p in art:
        print(f"  - {p}")
