import os
import requests
import aiohttp
import aiofiles


def determine_url_type(url):
    if "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url or "vt.tiktok.com" in url:
        return "tiktok"
    else:
        return None


def get_instagram_media(url):
    api_key = "024a509a11a3c90b229edb7052ed4fe5"
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


async def download_video(video_link: str, destination: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_link) as response:
                if response.status == 200:
                    async with aiofiles.open(f'videos/{destination}.mp4', 'wb') as video_file:
                        await video_file.write(await response.read())

                return True
    except Exception as e:
        print(e)

    return False
