import requests

def searchGiphy(query, apiKey, limit=5, offset=0):
    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        "api_key": apiKey,
        "q": query,
        "limit": limit,
        "offset": offset,
        "rating": "pg",
        "lang": "en"
    }

    response = requests.get(url, params=params)
    results = []

    if response.status_code == 200:
        data = response.json()
        for gif in data["data"]:
            previewUrl = gif["images"]["downsized"]["url"]
            fullGifUrl = gif["images"]["original"]["url"]
            results.append((previewUrl, fullGifUrl))

    return results