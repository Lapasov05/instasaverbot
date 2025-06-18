import logging
import os
from aiogram import Bot, Dispatcher, types, F
import instaloader
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaVideo, InputMediaPhoto
from config import API_TOKEN, CHANNEL_ID
from database import insert_data, update_statistics, check_chat_id_exists, get_user_role, get_statistics, get_all_users
from functions.functions import get_instagram_media, determine_url_type, download_video, fetch_channel_info, \
    get_video_size, help_text_uz, help_text_en, welcome_uz, welcome_en
# from functions.instagramsaver_functions import instagram_saver
from functions.state import SendAnnouncement
from keyboard.keyboard import client_choice, share_with_friends, English_or_Uzbek, Admin_Button, all_users, \
    delete_keyboard, admin_choice

# API_TOKEN = "7451078333:AAFSbRXoMGw0HWbYvZ3wLx5abE6ucr5FQPw"
# print(type(API_TOKEN))
# CHANNEL_ID = '@english_movies_by_code'  # Replace with your channel ID

# Define constants for languages
LANG_UZBEK = 'uzbek'
LANG_ENGLISH = 'english'

# Dictionary to store user language preferences
user_languages = {}

logging.basicConfig(level=logging.INFO)
# print(f"API_TOKEN: {API_TOKEN}")  # This should print your token

bot = Bot(API_TOKEN)

# bot = Bot(API_TOKEN)
dp = Dispatcher()

L = instaloader.Instaloader()


def get_language(user_id):
    return user_languages.get(user_id, LANG_ENGLISH)  # Default to English if not set


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    # member_status = await bot.get_chat_member(CHANNEL_ID, user_id)
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
        await callback_query.message.answer(f"Bizning xizmatdan foydalanish uchun oldin kanalga obuna bo'ling 😊\n",
                                            reply_markup=reply_markup)
        await callback_query.message.delete()
    if member_status.status == 'member':
        await callback_query.message.answer(text=welcome_uz)
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
        await callback_query.message.answer(text=welcome_en)
        await callback_query.message.delete()


@dp.callback_query(lambda callback_query: callback_query.data == "check")
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
            await callback_query.message.answer(text=welcome_uz)
            await callback_query.message.delete()
        else:
            await callback_query.message.answer(text=welcome_en)
            await callback_query.message.delete()


@dp.message(lambda msg: msg.text == "/help")
async def help_command(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)

    if lang == LANG_UZBEK:
        await message.answer(text=help_text_uz)
    else:
        await message.answer(text=help_text_en)


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
            f"Username: @{username}\n"
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
        await message.answer(f"{msg}", reply_markup=reply_markup)
    else:
        await message.answer(f"{msg}", reply_markup=reply_markup)


@dp.callback_query(lambda callback_query: callback_query.data == 'confirm')
async def confirm(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    announcement_msg = data.get("announcement")
    users = get_all_users()  # Get all users from your database
    # print(users)
    total_users = len(users)
    # print(total_users)
    successful_sends = 0
    failed_sends = 0

    for user in users:
        chat_id = int(user['chat_id'])
        print(chat_id)  # Make sure 'chat_id' is a valid key
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
@dp.callback_query(lambda callback_query: callback_query.data == "all")
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
            try:
                member_status = await bot.get_chat_member(CHANNEL_ID, int(user['user_id']))
                following = '✅ Following' if member_status.status != 'left' else '❌ Not Following'
            except TelegramBadRequest:
                following = '❌ Unknown'

            user_list_text += (
                f"✨ *{idx}. Username*: `{username}`\n"
                f"   📅 *Joined*: `{created_date}`\n"
                f"   📡 *Status*: {following}\n\n"
            )
        reply_markup = delete_keyboard()
        await callback_query.message.answer(user_list_text, parse_mode="Markdown", reply_markup=reply_markup)
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
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id - 1)

        # Notify the user that the messages have been deleted
        await callback_query.message.answer("Deleted 📦")
    else:
        await callback_query.message.answer("🚫 This button is not for you.")


async def send_and_cleanup(message, send_func, loading_message, *args, **kwargs):
    await send_func(*args, **kwargs)
    await loading_message.delete()


@dp.message(F.text.startswith("https"))
async def handle_instagram_url(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)

    try:
        url = message.text.strip()
        loading_message = await message.answer("⌛️")  # Loading message
        url_type = determine_url_type(url)
        reply_markup = share_with_friends()
        caption_text = (
            "📥@Insta_Save_Video_bot orqali yuklab olindi" if lang == LANG_UZBEK
            else "📥Downloaded via @Insta_Save_Video_bot"
        )

        update_statistics(url_type)

        response = get_instagram_media(url)
        if url_type == 'instagram':
            # print(response)
            if not response:
                error_text = "Video yuklab olish vositasidan noto'g'ri javob." if lang == LANG_UZBEK else "Invalid response from the video downloader."
                await send_and_cleanup(message, message.answer, loading_message, error_text)
                return
            # Single media handling
            if 'download_url' in response:
                media_type = response['type']
                download_url = response.get('download_url')
                thumb_url = response.get('thumb')
                caption = response.get('caption')

                if media_type == 'video' and download_url:
                    video_size = await get_video_size(download_url)
                    print(video_size)
                    if video_size is None or video_size < 20971520:
                        print("hello video")
                        await send_and_cleanup(
                            message, message.answer_video, loading_message,
                            video=download_url, caption=caption_text, thumb=thumb_url
                        )
                    elif video_size >= 20971520:
                        filename = f'videos/{user_id}-{message.message_id}.mp4'
                        print(filename)
                        if await download_video(download_url, filename):
                            await send_and_cleanup(
                                message, message.answer_video, loading_message,
                                video=FSInputFile(filename), caption=f"{caption} \n{caption_text}", reply_markup=reply_markup,
                                thumb=thumb_url
                            )
                            os.remove(filename)
                    elif video_size is None or video_size < 20971520:
                        print("hello video")
                        await send_and_cleanup(
                            message, message.answer_video, loading_message,
                            video=download_url, caption=caption_text, thumb=thumb_url
                        )
                    else:
                        filename = f'videos/{user_id}-{message.message_id}.mp4'
                        if await download_video(download_url, filename):
                            await send_and_cleanup(
                                message, message.answer_video, loading_message,
                                video=FSInputFile(filename), caption=caption_text, reply_markup=reply_markup,
                                thumb=thumb_url
                            )
                            os.remove(filename)
                        else:
                            await send_and_cleanup(
                                message, message.answer, loading_message,
                                "Video yuklab olishda xatolik yuz berdi." if lang == LANG_UZBEK else "Failed to download the video."
                            )
                elif media_type == 'image' and download_url:
                    await send_and_cleanup(
                        message, message.answer_photo, loading_message,
                        download_url, caption=caption_text, reply_markup=reply_markup
                    )
                else:
                    error_text = "Qo'llab-quvvatlanmaydigan media turi." if lang == LANG_UZBEK else "Unsupported media type."
                    await send_and_cleanup(message, message.answer, loading_message, error_text)

            elif 'medias' in response:
                from aiogram.types import InputMediaPhoto

                # Extract media from response
                media_group = []
                caption = response['caption'] + "\n\n@Insta_Save_Video_bot orqali yuklab olindi"

                # Add images to media group
                for idx, media in enumerate(response['medias']):
                    # print(media)
                    if media['type'] == 'image':
                        if idx == 0:  # Add caption only to the first image
                            media_group.append(InputMediaPhoto(media=media['download_url'], caption=caption))
                        else:
                            media_group.append(InputMediaPhoto(media=media['download_url']))

                # Send media group
                await message.answer_media_group(media_group)

            else:
                error_text = "Video yuklab olish vositasidan noto'g'ri javob." if lang == LANG_UZBEK else "Invalid response from the video downloader."
                await send_and_cleanup(message, message.answer, loading_message, error_text)

        if url_type == 'tiktok':
            print(response)
        if url_type == 'youtube':
            print(response)
        if url_type == 'facebook':
            print(response)
        if url_type == 'twitter':
            print(response)
        if url_type == 'linkedin':
            print(response)
        if url_type == 'snapchat':
            print(response)
        if url_type == 'pinterest':
            print(response)
        if url_type == 'reddit':
            print(response)
        if url_type == 'tumblr':
            print(response)
        if url_type == 'whatsapp':
            print(response)
        if url_type == 'weibo':
            print(response)
        if url_type == 'twitch':
            print(response)

    except Exception as e:
        print("Error:", e)
        error_text = (
            "Video yoki rasmni yuklab olishda xatolik. Iltimos, URLni tekshiring va qayta urinib ko'ring."
            if lang == LANG_UZBEK else
            "Failed to download the video or image. Please check the URL and try again."
        )
        await send_and_cleanup(message, message.answer, loading_message, error_text)


# Handler for URLs starting with https://www
@dp.message(F.text.startswith("https:"))
async def handle_instagram_url(message: types.Message):
    user_id = message.from_user.id
    lang = get_language(user_id)

    try:
        url = message.text.strip()
        loading_message = await message.answer("⌛️")  # Loading message
        url_type = determine_url_type(url)
        reply_markup = share_with_friends()
        caption_text = (
            "📥@Insta_Save_Video_bot orqali yuklab olindi" if lang == LANG_UZBEK
            else "📥Downloaded via @Insta_Save_Video_bot"
        )

        # Update statistics
        if url_type in ["instagram", "tiktok"]:
            update_statistics(url_type)

        response = get_instagram_media(url)
        if not response:
            error_text = "Video yuklab olish vositasidan noto'g'ri javob." if lang == LANG_UZBEK else "Invalid response from the video downloader."
            await send_and_cleanup(message, message.answer, loading_message, error_text)
            return

        # Single media handling
        if 'download_url' in response:
            media_type = response['type']
            download_url = response.get('download_url')
            thumb_url = response.get('thumb')
            caption = response.get('caption')

            if media_type == 'video' and download_url:
                video_size = await get_video_size(download_url)
                print(video_size)
                if video_size is None or video_size < 20971520:
                    print("hello video")
                    await send_and_cleanup(
                        message, message.answer_video, loading_message,
                        video=download_url, caption=f"{caption} \n{caption_text}", thumb=thumb_url
                    )
                elif video_size >= 20480:
                    filename = f'videos/{user_id}-{message.message_id}.mp4'
                    print(filename)
                    if await download_video(download_url, filename):
                        await send_and_cleanup(
                            message, message.answer_video, loading_message,
                            video=FSInputFile(filename), caption=caption_text, reply_markup=reply_markup,
                            thumb=thumb_url
                        )
                        os.remove(filename)
                elif video_size is None or video_size < 20971520:
                    print("hello video")
                    await send_and_cleanup(
                        message, message.answer_video, loading_message,
                        video=download_url, caption=caption_text, thumb=thumb_url
                    )
                else:
                    filename = f'videos/{user_id}-{message.message_id}.mp4'
                    if await download_video(download_url, filename):
                        await send_and_cleanup(
                            message, message.answer_video, loading_message,
                            video=FSInputFile(filename), caption=caption_text, reply_markup=reply_markup,
                            thumb=thumb_url
                        )
                        os.remove(filename)
                    else:
                        await send_and_cleanup(
                            message, message.answer, loading_message,
                            "Video yuklab olishda xatolik yuz berdi." if lang == LANG_UZBEK else "Failed to download the video."
                        )
            elif media_type == 'image' and download_url:
                await send_and_cleanup(
                    message, message.answer_photo, loading_message,
                    download_url, caption=caption_text, reply_markup=reply_markup
                )
            else:
                error_text = "Qo'llab-quvvatlanmaydigan media turi." if lang == LANG_UZBEK else "Unsupported media type."
                await send_and_cleanup(message, message.answer, loading_message, error_text)

        # Multiple media handling
        # Multiple media handling
        elif 'medias' in response:
            from aiogram.types import InputMediaPhoto

            # Extract media from response
            media_group = []
            caption = response['caption'] + "\n\n@Insta_Save_Video_bot orqali yuklab olindi"

            # Add images to media group
            for idx, media in enumerate(response['medias']):
                # print(media)
                if media['type'] == 'image':
                    if idx == 0:  # Add caption only to the first image
                        media_group.append(InputMediaPhoto(media=media['download_url'], caption=caption))
                    else:
                        media_group.append(InputMediaPhoto(media=media['download_url']))

            # Send media group
            await message.answer_media_group(media_group)

        else:
            error_text = "Video yuklab olish vositasidan noto'g'ri javob." if lang == LANG_UZBEK else "Invalid response from the video downloader."
            await send_and_cleanup(message, message.answer, loading_message, error_text)

    except Exception as e:
        print("Error:", e)
        error_text = (
            "Video yoki rasmni yuklab olishda xatolik. Iltimos, URLni tekshiring va qayta urinib ko'ring."
            if lang == LANG_UZBEK else
            "Failed to download the video or image. Please check the URL and try again."
        )
        await send_and_cleanup(message, message.answer, loading_message, error_text)


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
