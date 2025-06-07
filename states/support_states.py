from aiogram.fsm.state import StatesGroup, State

class SupportStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_response = State()
