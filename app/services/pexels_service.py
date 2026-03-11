import requests
import random
import os

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def build_query(product, tone):

    keywords = {

    # Technology / Coding
    "coding": "programming laptop workspace developer coding screen",
    "programming": "software developer coding laptop desk",
    "developer": "software engineer coding workspace",
    "tech": "modern technology workspace computer setup",
    "ai": "artificial intelligence computer technology lab",
    "startup": "startup office laptop working team",

    # Gaming
    "gaming": "gaming computer rgb setup gamer desk",
    "esports": "esports gaming computer setup",
    "streaming": "streamer gaming desk setup",

    # Fitness
    "gym": "fitness gym workout training exercise",
    "fitness": "workout training gym fitness lifestyle",
    "yoga": "yoga meditation wellness practice",

    # Lifestyle
    "lifestyle": "modern lifestyle coffee shop working laptop",
    "daily": "daily routine lifestyle workspace",
    "productivity": "productive workspace laptop working",
    "minimal": "minimal desk aesthetic workspace",

    # Business
    "business": "business meeting laptop office workspace",
    "entrepreneur": "entrepreneur laptop working office",
    "marketing": "digital marketing laptop working desk",
    "finance": "finance business laptop analytics workspace",

    # Education
    "education": "student studying laptop desk learning",
    "study": "student studying workspace laptop books",
    "online learning": "online learning laptop study desk",

    # Travel
    "travel": "travel lifestyle laptop remote work",
    "remote work": "digital nomad laptop working cafe",

    # Fashion
    "fashion": "fashion lifestyle studio creative work",
    "beauty": "beauty lifestyle product workspace",

    # Food
    "food": "food cooking kitchen preparation lifestyle",
    "cooking": "chef cooking kitchen preparation",

    # Creative
    "design": "creative designer workspace laptop graphics",
    "photography": "photographer editing photos laptop",
    "video editing": "video editing computer workstation",

}

    tone_phrase = keywords.get(tone.lower(), tone)
    
    query = f"{product} {tone_phrase}"

    print("Pexels search query:", query)

    return query


def search_videos(product, tone):

    query = build_query(product, tone)

    url = "https://api.pexels.com/videos/search"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": 20
    }

    response = requests.get(url, headers=headers, params=params)

    videos = response.json()["videos"]

    # filter videos that mention product keyword
    filtered = []

    for v in videos:
        url = v["url"].lower()

        if product.lower().split()[0] in url:
            filtered.append(v)

    # fallback if nothing found
    if len(filtered) < 3:
        filtered = videos

    videos = filtered

    return random.sample(videos, 3)

def get_best_video_file(video):

    # Prefer HD quality
    for file in video["video_files"]:
        if file.get("quality") == "hd":
            return file["link"]

    # fallback to first file
    return video["video_files"][0]["link"]


def download_video(url, filename):

    cache_dir = "cache/clips"

    os.makedirs(cache_dir, exist_ok=True)

    filepath = os.path.join(cache_dir, filename)

    # If already cached → reuse
    if os.path.exists(filepath):
        print("Using cached clip:", filepath)
        return filepath

    # Otherwise download
    print("Downloading clip:", filename)

    r = requests.get(url)

    with open(filepath, "wb") as f:
        f.write(r.content)

    return filepath

def safe_search(product, tone):

    # try product + tone
    videos = search_videos(product + " " + tone, "")

    if videos:
        return videos

    # fallback tone only
    videos = search_videos("", tone)

    if videos:
        return videos

    # final fallback generic
    videos = search_videos("", "lifestyle")

    return videos