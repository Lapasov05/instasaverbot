from aiogram.fsm.state import State, StatesGroup

class SendAnnouncement(StatesGroup):
    announcement = State()
