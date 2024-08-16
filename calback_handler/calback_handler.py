# from aiogram import types
# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery
# from main import dp, bot
# from database import get_all_users, update_statistics
# import logging
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
#
# @dp.callback_query(lambda callback_query: callback_query.data == 'confirm')
# async def confirm(callback_query: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     announcement_msg = data.get("announcement")
#     users = get_all_users()  # Get all users from your database
#     total_users = len(users)
#     print(total_users)
#     successful_sends = 0
#     failed_sends = 0
#
#     for user in users:
#         try:
#             print("davay")
#             await bot.send_message(user['chat_id'], announcement_msg)
#             successful_sends += 1
#         except Exception as e:
#             logging.error(f"Failed to send message to {user['chat_id']}: {e}")
#             failed_sends += 1
#
#
#     # Clear the state and notify the admin
#     await state.clear()
#     await callback_query.message.answer(
#         f"📤 Announcement sent successfully!\n\n"
#         f"👥 Total Users: {total_users}\n"
#         f"✅ Sent: {successful_sends}\n"
#         f"❌ Failed: {failed_sends}"
#     )
#     await callback_query.message.delete()
