"""
Системы состояний (FSM) для бота
"""
from aiogram.fsm.state import State, StatesGroup

class TestState(StatesGroup):
    """Состояния для теста определения специальности"""
    waiting_for_answer = State()

class CourseState(StatesGroup):
    """Состояния для выбора и работы с курсами"""
    selecting_course = State()
    viewing_course = State()
    enrolling = State()

class ProgressState(StatesGroup):
    """Состояния для отслеживания прогресса"""
    updating_progress = State()
