import requests, os

import os

API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_videos(query, max_results=2):
    """
    Fetch YouTube videos for a specific query
    """
    url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&q={query}&maxResults={max_results}&type=video&key={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    
    videos = []
    for item in data.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            "videoId": item["id"]["videoId"]
        })
    return videos
