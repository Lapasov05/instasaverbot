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
    # api_key = "024a509a11a3c90b229edb7052ed4fe5"
    api_key = "ddd589012f161808afc7bd6d6a004761"
    # print(api_key)

    base_url = "https://apishop.uz/apikey.php"
    params = {
        'status': 'media',
        'url': url,
        'apikey': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        # response.raise_for_status()
        # print(response.json())
        return response.json()
    except requests.RequestException as e:
        # print(f"Xato yuz berdi: {e}")
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


async def get_video_size(download_url):
    async with aiohttp.ClientSession() as session:
        async with session.head(download_url) as resp:
            if resp.status == 200:
                return int(resp.headers.get('Content-Length', 0))
            return 0



