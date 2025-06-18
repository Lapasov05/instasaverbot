from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def client_choice():
    confirm_btn=InlineKeyboardButton(text="Kanalimiz 🎥",callback_data="english_movies",url="https://t.me/english_movies_by_code")
    check=InlineKeyboardButton(text="♻Tekshirish♻️",callback_data="check")
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[confirm_btn],[check]])
    return reply_markup


def share_with_friends():
    share_btn = InlineKeyboardButton(
        text="Share with Friends",
        url="https://t.me/share/url?url=https://t.me/instatik_saverbot&text=Biz%20bilan%20oson%20yuklang"
    )
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[share_btn]])
    return reply_markup



def English_or_Uzbek():
    uzbek_btn=InlineKeyboardButton(text="🇺🇿Uzbek",callback_data="uzbek")
    eng_btn=InlineKeyboardButton(text="🇺🇸English",callback_data="english")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[uzbek_btn, eng_btn]], one_time_keyboard=True)
    return reply_markup



def Admin_Button():
    statistics_btn=KeyboardButton(text="📊Show statiscs📊")
    users_list_btn=KeyboardButton(text="👥Show Users👥")
    send_announcement=KeyboardButton(text="📤Send Announcement📤")
    my_channel=KeyboardButton(text="🎥My channel🎥")
    reply_markup=ReplyKeyboardMarkup(keyboard=[[statistics_btn,users_list_btn],[send_announcement,my_channel]],resize_keyboard=True,one_time_keyboard=True)
    return reply_markup


# Function to generate inline keyboard
def generate_pagination_keyboard(current_page, total_pages):
    keyboard = InlineKeyboardMarkup(row_width=3)
    if current_page > 1:
        keyboard.insert(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{current_page-1}"))
    if current_page < total_pages:
        keyboard.insert(InlineKeyboardButton("Next ➡️", callback_data=f"page_{current_page+1}"))
    return keyboard

# Function to get a slice of users
def get_user_slice(users, page, page_size=10):
    start = (page - 1) * page_size
    end = start + page_size
    return users[start:end]



def all_users():
    share_btn = InlineKeyboardButton(
        text="All users",
        callback_data="all"
    )
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[share_btn]])
    return reply_markup


def delete_keyboard():
    share_btn = InlineKeyboardButton(
        text="delete",
        callback_data="delete_all"
    )
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[share_btn]])
    return reply_markup



def admin_choice():
    confirm_btn=InlineKeyboardButton(text="✅Confirm",callback_data="confirm")
    cancel_btn=InlineKeyboardButton(text="❌Cancel",callback_data="cancel")
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[confirm_btn,cancel_btn]])
    return reply_markup
