import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
import instaloader
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from config import API_TOKEN, CHANNEL_ID
from database import insert_data, update_statistics, check_chat_id_exists, get_user_role, get_statistics, get_all_users
from functions.functions import get_instagram_media, determine_url_type, download_video, fetch_channel_info, get_video_size
from functions.state import SendAnnouncement
from keyboard.keyboard import client_choice, share_with_friends, English_or_Uzbek, Admin_Button, all_users, \
    delete_keyboard, admin_choice

# API_TOKEN = "7451078333:AAFSbRXoMGw0HWbYvZ3wLx5abE6ucr5FQPw"
print(type(API_TOKEN))
# CHANNEL_ID = '@english_movies_by_code'  # Replace with your channel ID

# Define constants for languages
LANG_UZBEK = 'uzbek'
LANG_ENGLISH = 'english'

# Dictionary to store user language preferences
user_languages = {}

logging.basicConfig(level=logging.INFO)
print(f"API_TOKEN: {API_TOKEN}")  # This should print your token

bot = Bot(API_TOKEN)

# bot = Bot(API_TOKEN)
dp = Dispatcher()

# Initialize Instaloader
L = instaloader.Instaloader()

def get_language(user_id):
    return user_languages.get(user_id, LANG_ENGLISH)  # Default to English if not set


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    member_status = await bot.get_chat_member(CHANNEL_ID, user_id)
    chat_id = message.from_user.id
    user_role = get_user_role(chat_id)  # Function to get the role_id
    username = message.from_user.first_name
    reply_markup = Admin_Button()


    if user_role == 2:
        # If role_id is 2, send admin message
        await message.answer(f"Assalomu alaykum Admin {username}", reply_markup=reply_markup)
        return


    uzbek_english = English_or_Uzbek()
    await message.answer("""🤖⚙️\t\n🇺🇸Please choose your language!\n 🇺🇿 Iltimos bot tilini sozlang!""",
                         reply_markup=uzbek_english)

    if not check_chat_id_exists(chat_id):
        insert_data({'username': username, 'chat_id': chat_id, "user_id": user_id})


@dp.callback_query(lambda callback_query: callback_query.data == LANG_UZBEK)
async def select_uzbek(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_languages[user_id] = LANG_UZBEK
    member_status = await bot.get_chat_member(CHANNEL_ID, user_id)

    if member_status.status == 'left':
        reply_markup = client_choice()
        await callback_query.message.answer(f"Bizning xizmatdan foydalanish uchun oldin kanalga obuna bo'ling 😊\n", reply_markup=reply_markup)
        await callback_query.message.delete()
    if member_status.status == 'member':
        await callback_query.message.answer(f"""Botga Xush kelibsiz! 
    Bizning xizmatlar

    📲 Instagram

    📲  Tiktok  
    
    ⌛️  url (Havolani)   jo'nating   va  siz  qisqa  vaqt  ichida   videoni   qabul  qiling""")
        await callback_query.message.delete()


@dp.callback_query(lambda callback_query: callback_query.data == LANG_ENGLISH)
async def select_english(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_languages[user_id] = LANG_ENGLISH
    member_status = await bot.get_chat_member(CHANNEL_ID, user_id)

    if member_status.status == 'left':
        reply_markup = client_choice()
        await callback_query.message.answer(f"Please follow our channel to use our bot 😊\n", reply_markup=reply_markup)
        await callback_query.message.delete()
    if member_status.status == 'member':
        await callback_query.message.answer(f"""Welcome to our bot! 
    Our services:

    📲 Instagram

    📲  Tiktok  

    ⌛️ Send the URL and receive the video shortly""")
        await callback_query.message.delete()


@dp.callback_query(lambda callback_query: callback_query.data =="check")
async def check_user(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    member_status = await bot.get_chat_member(CHANNEL_ID, user_id)
    lang = get_language(user_id)
    print(lang)

    if member_status.status == 'left':
        reply_markup = client_choice()

        if lang == LANG_UZBEK:
            await callback_query.answer(f"Siz kanalga obuna bolmadingiz 😢\n",
                                        reply_markup=reply_markup)
        else:
            await callback_query.answer(f"You do not follow our channel 😢\n",
                                        reply_markup=reply_markup)



    if member_status.status == 'member':

        if lang == LANG_UZBEK:
            await callback_query.message.answer(f"""Botga Xush kelibsiz! 
    Bizning xizmatlar

    📲 Instagram

    📲  Tiktok  

    ⌛️  url (Havolani)   jo'nating   va  siz  qisqa  vaqt  ichida   videoni   qabul  qiling""")
            await callback_query.message.delete()
        else:
            await callback_query.message.answer(f"""Welcome to our bot! 
            Our services:
    
            📲 Instagram
    
            📲  Tiktok  
    
            ⌛️ Send the URL and receive the video shortly""")
            await callback_query.message.delete()


@dp.message(lambda msg: msg.text == "/help")
async def help_command(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)


    if lang == LANG_UZBEK:
        await message.answer("Bu bot orqali siz Instagramdagi video, istoriya va postlarni yuklab olishingiz mumkin.\n"
                             "Botni ishlating va zavqlaning")
    else:
        await message.answer("With this bot, you can download videos, stories, and posts from Instagram.\n"
                             "Use the bot and enjoy!")



@dp.message(lambda msg: msg.text == "🎥My channel🎥")
async def my_channel(message: types.Message, state: FSMContext):
    try:
        # Fetch and update channel info
        channel_info = await fetch_channel_info()

        title = channel_info.get('title', 'Unknown')
        username = channel_info.get('username', 'Unknown')
        invite_link = channel_info.get('invite_link', 'No invite link')
        photo_file_id = channel_info.get('photo', 'No photo')

        # Send channel info to the user
        response_text = (
            f"📊 Channel Information:\n"
            f"Title: {title}\n"
            f"Username: {username}\n"
            # f"Invite link: {invite_link}\n"
        )


        await message.answer(response_text)

    except Exception as e:
        logging.error(f"An error occurred while fetching channel information: {e}")
        await message.answer(f"An error occurred while fetching channel information: {e}")


@dp.message(lambda msg: msg.text == "📤Send Announcement📤")
async def send_announcement(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_language(user_id)
    if lang == LANG_UZBEK:
        await message.answer("📨Send message: ")
        await state.set_state(SendAnnouncement.announcement)
    else:
        await message.answer("📨Xabarni jo'nating: ")
        await state.set_state(SendAnnouncement.announcement)




@dp.message(SendAnnouncement.announcement)
async def Announcement(message: types.Message, state: FSMContext):
    result = message.text
    await state.update_data({
        "announcement": result
    })
    user_id = message.from_user.id
    lang = get_language(user_id)
    reply_markup = admin_choice()
    data = await state.get_data()
    msg = data['announcement']
    if lang == LANG_UZBEK:
        await message.answer(f"{msg}",reply_markup=reply_markup)
    else:
        await message.answer(f"{msg}",reply_markup=reply_markup)



@dp.callback_query(lambda callback_query: callback_query.data == 'confirm')
async def confirm(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    announcement_msg = data.get("announcement")
    users = get_all_users()  # Get all users from your database
    print(users)
    total_users = len(users)
    print(total_users)
    successful_sends = 0
    failed_sends = 0

    for user in users:
        chat_id = int(user['chat_id'])
        print(chat_id)# Make sure 'chat_id' is a valid key
        try:
            await bot.send_message(chat_id, announcement_msg)
            successful_sends += 1
        except Exception as e:
            logging.error(f"Failed to send message to {user['chat_id']}: {e}")
            failed_sends += 1


    # Clear the state and notify the admin
    await state.clear()
    await callback_query.message.answer(
        f"📤 Announcement sent successfully!\n\n"
        f"👥 Total Users: {total_users}\n"
        f"✅ Sent: {successful_sends}\n"
        f"❌ Failed: {failed_sends}"
    )
    await callback_query.message.delete()


@dp.callback_query(lambda callback_query: callback_query.data == 'cancel')
async def cancel(callback_query: CallbackQuery, state: FSMContext):
    # Clear the state and notify the admin
    await state.clear()
    await callback_query.message.answer(
        "🚫 Announcement sending process has been canceled."
    )
    await callback_query.message.delete()

@dp.message(lambda msg: msg.text == "📊Show statiscs📊")
async def show_statistics(message: types.Message):
    chat_id = message.from_user.id
    user_role = get_user_role(chat_id)  # Function to get the role_id

    if user_role == 2:
        # Fetch the statistics
        instagram_count, tiktok_count = get_statistics()

        # Create a modern and stylish response
        stats_message = (
            f"✨ Bot Statistics ✨\n\n"
            f"🔍 Here’s what we've collected so far: \n\n"
            f"📸 Instagram: {instagram_count}  downloads 📥\n"
            f"🎥 Tiktok:  {tiktok_count}  downloads 📥\n\n"
            f"📊 Keep those URLs coming! 🚀"
        )
        await message.answer(stats_message)
    else:
        await message.answer("⛔️ This button is not for you.")




@dp.message(lambda msg: msg.text == "👥Show Users👥")
async def show_users_overview(message: types.Message):
    chat_id = message.from_user.id
    user_role = get_user_role(chat_id)

    if user_role == 2:
        users = get_all_users()  # Assuming this is a synchronous function
        total_users = len(users)

        # Initialize following users count
        following_users = 0

        # Count how many users are following the channel
        for user in users:
            try:
                member_status = await bot.get_chat_member(CHANNEL_ID, user['chat_id'])
                if member_status.status not in ['left', 'kicked']:
                    following_users += 1
            except Exception as e:
                logging.error(f"Error checking member status for user {user['chat_id']}: {e}")

        user_list_text = (
            f"👥 **User Overview** 👥\n\n"
            f"🌍 *Total Users*: {total_users}\n"
            f"📡 *Currently Following*: {following_users} users\n\n"
        )

        show_users_button = all_users()
        await message.answer(user_list_text, reply_markup=show_users_button, parse_mode="Markdown")
    else:
        await message.answer("🚫 This button is not for you.")



# Callback handler to display users with pagination
@dp.callback_query(lambda callback_query: callback_query.data =="all")
async def show_users(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_role = get_user_role(chat_id)


    if user_role == 2:
        users = get_all_users()
        print(users)
        user_list_text = f"👥 **All users** 👥\n\n"

        for idx, user in enumerate(users):
            username = user['username'] or "No Username"
            # Assuming user['created_date'] is already a datetime object
            created_date = user['created_date']
            member_status = await bot.get_chat_member(CHANNEL_ID, user['user_id'])
            following = '✅ Following' if member_status.status != 'left' else '❌ Not Following'

            user_list_text += (
                f"✨ *{idx}. Username*: `{username}`\n"
                f"   📅 *Joined*: `{created_date}`\n"
                f"   📡 *Status*: {following}\n\n"
            )
        reply_markup = delete_keyboard()
        await callback_query.message.answer(user_list_text, parse_mode="Markdown",reply_markup=reply_markup)
    else:
        await callback_query.message.answer("🚫 This button is not for you.")


@dp.callback_query(lambda callback_query: callback_query.data == "delete_all")
async def delete_messages(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    user_role = get_user_role(chat_id)

    if user_role == 2:
        # Delete the last message sent by the bot (i.e., the message containing the button)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

        # Delete the last message sent by the user
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id - 1)

        # Notify the user that the messages have been deleted
        await callback_query.message.answer("Deleted 📦")
    else:
        await callback_query.message.answer("🚫 This button is not for you.")


@dp.message()
async def handle_instagram_url(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    member_status = await bot.get_chat_member(CHANNEL_ID, user_id)

    if member_status.status == 'left':
        if lang == LANG_UZBEK:
            await message.answer(f"Iltimos, botimizdan foydalanishdan oldin {CHANNEL_ID} kanaliga obuna bo'ling.")
        else:
            await message.answer(f"Please follow our channel {CHANNEL_ID} first to use this bot.")
        return

    try:
        url = message.text.strip()
        loading_message = await message.answer("⌛️")  # Store the loading message
        print("url keldi")
        url_type = determine_url_type(url)
        reply_markup = share_with_friends()
        caption_text = "📥@Insta_Save_Video_bot orqali yuklab olindi" if lang == LANG_UZBEK else "📥Downloaded via @Insta_Save_Video_bot"

        if url_type == "instagram":
            print("instagram")
            update_statistics('instagram')
        elif url_type == "tiktok":
            print("tiktok")
            update_statistics("tiktok")
        response = get_instagram_media(url)
        if 'download_url' in response:
            result = response['type']
            download_url = response.get('download_url')
            thumb_url = response.get('thumb')
            if result == 'video':
                if download_url:
                    video_size = await get_video_size(download_url)
                    print(video_size)
                    if video_size < 20971520:
                        print("20 mb kam")
                        await message.answer_video(video=download_url,caption=caption_text,thumb=thumb_url)
                        return
                    else:
                        is_downloaded = await download_video(download_url, str(message.from_user.id) + '-' + str(message.message_id))
                    if is_downloaded:
                        await message.answer_video(video=FSInputFile('videos/' + str(message.from_user.id) + '-' + str(message.message_id) + '.mp4'), caption=caption_text, reply_markup=reply_markup,
                                                   thumb=thumb_url)
                        video_path = f'videos/{str(message.from_user.id)}-{str(message.message_id)}.mp4'
                        print(video_path)
                        os.remove(video_path)
                    else:
                        pass  # not downloaded error
                else:
                    if lang == LANG_UZBEK:
                        await message.answer("Video URL javobda topilmadi.")
                    else:
                        await message.answer("Video URL not found in the response.")
            elif result == 'image':
                if download_url:
                    await message.answer_photo(download_url, caption=caption_text, reply_markup=reply_markup)
                else:
                    if lang == LANG_UZBEK:
                        await message.answer("Rasm URL javobda topilmadi.")
                    else:
                        await message.answer("Image URL not found in the response.")
        elif "medias" in response:
            for media in response['medias']:
                if media['type'] == "image":
                    await message.answer_photo(media['download_url'], caption=caption_text, reply_markup=reply_markup)
                await message.answer_video(media['download_url'], caption=caption_text, reply_markup=reply_markup)
            else:
                if lang == LANG_UZBEK:
                    await message.answer("Qo'llab-quvvatlanmaydigan media turi.")
                else:
                    await message.answer("Unsupported media type.")
        else:
            if lang == LANG_UZBEK:
                await message.answer("Video yuklab olish vositasidan noto'g'ri javob.")
            else:
                await message.answer("Invalid response from the video downloader.")

        await loading_message.delete()  # Delete the loading message after the final response

    except Exception as e:
        print("Error:",e)
        if lang == LANG_UZBEK:
            await message.answer(
                "Video yoki rasmni yuklab olishda xatolik. Iltimos, URLni tekshiring va qayta urinib ko'ring.")
        else:
            await message.answer("Failed to download the video or image. Please check the URL and try again.")

        await loading_message.delete()  # Delete the loading message in case of an error




# @dp.message()
# async def handle_instagram_url(message: types.Message):
#     user_id = message.from_user.id
#     member_status = await bot.get_chat_member(CHANNEL_ID, user_id)
#
#     if member_status.status == 'left':
#         await message.answer(f"Please follow our channel {CHANNEL_ID} first to use this bot.")
#         return
#
#     try:
#         url = message.text.strip()
#         response = video_downloader(url)
#         reply_markup = share_with_friends()
#         caption_text = "@Insta_Save_Video_bot orqali yuklab olindi"
#         if 'result' in response:
#             result = response['result']
#             if result['is_video']:
#                 video_url = result.get('video_url')
#                 if video_url:
#                     await message.answer_video(video_url, caption=caption_text, reply_markup=reply_markup)
#                 else:
#                     await message.answer("Video URL not found in the response.")
#             else:
#                 image_url = result.get('image_url')
#                 if image_url:
#                     await message.answer_photo(image_url, caption=caption_text, reply_markup=reply_markup)
#                 else:
#                     await message.answer("Image URL not found in the response.")
#         else:
#             await message.answer("Invalid response from the video downloader.")
#     except Exception as e:
#         logging.error(e)
#         await message.answer("Failed to download the video or image. Please check the URL and try again.")


# @dp.message(lambda msg: msg.text == "/help")
# async def help_command(message : types.Message):
#     await message.answer("Bu bot orqali siz Instagramdagi video, istoriya va postlarni yuklab olishingiz mumkin.\n"
#                          "Botni ishlating va zavqlaning")
#


if __name__ == '__main__':
    dp.run_polling(bot)
