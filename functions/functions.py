import os
import requests


def determine_url_type(url):
    if "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url or "vt.tiktok.com" in url:
        return "tiktok"
    else:
        return None


def get_instagram_media(url):
    api_key = "024a509a11a3c90b229"
    print(api_key)

    base_url = "https://apishop.uz/apikey.php"
    params = {
        'status': 'media',
        'url': url,
        'apikey': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        # response.raise_for_status()
        print(response.json())
        return response.json()
    except requests.RequestException as e:
        print(f"Xato yuz berdi: {e}")
        return None
