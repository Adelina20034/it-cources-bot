"""
Системы состояний (FSM) для бота
"""
from aiogram.fsm.state import State, StatesGroup

class TestState(StatesGroup):
    """Состояния для теста определения специальности"""
    waiting_for_answer = State()

