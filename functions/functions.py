import os
import requests
import aiohttp
import aiofiles
from database import update_channel_info
from config import API_TOKEN, CHANNEL_ID


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

async def fetch_channel_info():
    api_url = f"https://api.telegram.org/bot{API_TOKEN}/getChat?chat_id={CHANNEL_ID}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            data = await response.json()

            if data.get('ok'):
                chat_info = data['result']
                print(chat_info)
                # Extract relevant information
                title = chat_info.get('title', 'Unknown')
                username = chat_info.get('username', 'Unknown')
                invite_link = chat_info.get('invite_link', 'No invite link')
                photo = chat_info.get('photo', {}).get('big_file_id', 'No photo')
                print(photo)

                return {
                    'title': title,
                    'username': username,
                    'description': chat_info.get('description', 'No description'),
                    'invite_link': invite_link,
                    'photo': photo
                }
            else:
                raise Exception("Failed to fetch channel info")




async def get_video_size(url: str) -> int:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                if response.status == 200:
                    # Get the size from the Content-Length header
                    size = response.headers.get('Content-Length')
                    return int(size) if size else None
                else:
                    print(f"Failed to get size. Status code: {response.status}")
    except Exception as e:
        print(f"Error fetching video size: {e}")
    return None