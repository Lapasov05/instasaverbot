import requests
import aiohttp
import aiofiles
import certifi
import ssl
from config import API_TOKEN, CHANNEL_ID


def determine_url_type(url):
    if "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url or "vt.tiktok.com" in url:
        return "tiktok"
    elif "facebook.com" in url or "fb.com" in url:
        return "facebook"
    elif "twitter.com" in url or "t.co" in url:
        return "twitter"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "linkedin.com" in url:
        return "linkedin"
    elif "snapchat.com" in url:
        return "snapchat"
    elif "pinterest.com" in url:
        return "pinterest"
    elif "reddit.com" in url:
        return "reddit"
    elif "tumblr.com" in url:
        return "tumblr"
    elif "whatsapp.com" in url:
        return "whatsapp"
    elif "telegram.me" in url or "t.me" in url:
        return "telegram"
    elif "weibo.com" in url:
        return "weibo"
    elif "twitch.tv" in url:
        return "twitch"
    else:
        return None


def get_instagram_media(url_video):
    api_key = "cf185636050b989e86f27e57e4139091"
    api_url = f"https://apishop.uz/apikey.php?status=media&url={url_video}&apikey={api_key}"
    try:
        response = requests.get(api_url)
        print(response.json())
        return response.json()
    except requests.RequestException as e:
        print(f"Xato yuz berdi: {e}")
        return None


async def download_video(video_link: str, destination: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_link, ssl=False) as response:
                if response.status == 200:
                    async with aiofiles.open(f'videos/{destination}.mp4', 'wb') as video_file:
                        await video_file.write(await response.read())
                    return True
    except Exception as e:
        print(e)
    return False


async def get_video_size(url: str) -> int:
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    size = response.headers.get('Content-Length')
                    print(size)
                    return int(size) if size else None
                else:
                    print(f"Failed to get size. Status code: {response.status}")
    except Exception as e:
        print(f"Error fetching video size: {e}")


async def fetch_channel_info():
    api_url = f"https://api.telegram.org/bot{API_TOKEN}/getChat?chat_id={CHANNEL_ID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            data = await response.json()
            if data.get('ok'):
                chat_info = data['result']
                return {
                    'title': chat_info.get('title', 'Unknown'),
                    'username': chat_info.get('username', 'Unknown'),
                    'description': chat_info.get('description', 'No description'),
                    'invite_link': chat_info.get('invite_link', 'No invite link'),
                    'photo': chat_info.get('photo', {}).get('big_file_id', 'No photo')
                }
            else:
                raise Exception("Failed to fetch channel info")


help_text_uz = """\
📥 Instagramdan kontent yuklab oling!  

Ushbu bot orqali osonlik bilan yuklab olishingiz mumkin:  
🎬 Videolar  
📖 Hikoyalar  
🖼 Postlar  

🚀 Botdan foydalaning va qulay yuklab olishdan zavqlaning!
"""

help_text_en = """\
📥 Download Instagram Content Effortlessly!  

With this bot, you can easily download:  
🎬 Videos  
📖 Stories  
🖼 Posts  

🚀 Just use the bot and enjoy hassle-free downloading!
"""

welcome_en = """\
🎉 Welcome to the Bot! 🎉  

👋 Enjoy our services and download your favorite videos quickly!  

🔗 Platforms:  
📸 Instagram — Download your favorite reels and posts!  
🎵 TikTok — Instantly download trending videos!  

🚀 It’s super easy to use!  
1️⃣ Send the URL (link).  
2️⃣ Your video will be ready in just a few seconds!
"""

welcome_uz = """\
🎉 Botga Xush kelibsiz! 🎉  

👋 Bizning xizmatlarimizdan foydalaning va sevimli videolaringizni tezda yuklab oling!  

🔗 Platformalar:  
📸 Instagram — Sevimli reel va postlaringizni yuklab oling!  
🎵 TikTok — Trenddagi videolarni bir zumda yuklab oling!  

🚀 Foydalanish juda oson!  
1️⃣ URL (havolani) yuboring.  
2️⃣ Bir necha soniyada videongiz tayyor bo'ladi!
"""
