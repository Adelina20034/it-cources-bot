"""
Клавиатуры и меню для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import SPECIALTY_TEST, COURSES_DATA

def get_specialty_keyboard() -> InlineKeyboardMarkup:
    """
    Получить клавиатуру для тестирования специальности
    Используем текущий вопрос из SPECIALTY_TEST
    """
    # SPECIALTY_TEST - это список вопросов
    # Когда нужен конкретный вопрос, его индекс передается через state
    
    # Для первого вопроса берем первый элемент
    if not SPECIALTY_TEST or len(SPECIALTY_TEST) == 0:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Вопросы не загружены", callback_data="test_error")]
        ])
    
    # Получаем первый вопрос (он будет обновляться в обработчике)
    current_question = SPECIALTY_TEST[0]
    
    buttons = []
    for answer_text, specialty_id in current_question['answers'].items():
        buttons.append([
            InlineKeyboardButton(text=answer_text, callback_data=f"test_{specialty_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_specialty_keyboard_for_question(question_index: int) -> InlineKeyboardMarkup:
    """
    Получить клавиатуру для конкретного вопроса теста
    
    Args:
        question_index: Индекс вопроса (0-6)
    
    Returns:
        InlineKeyboardMarkup с вариантами ответов
    """
    if not SPECIALTY_TEST or question_index >= len(SPECIALTY_TEST):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Вопрос не найден", callback_data="test_error")]
        ])
    
    current_question = SPECIALTY_TEST[question_index]
    
    buttons = []
    for answer_text, specialty_id in current_question['answers'].items():
        buttons.append([
            InlineKeyboardButton(text=answer_text, callback_data=f"test_{specialty_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_course_detail_keyboard(course_id: str) -> InlineKeyboardMarkup:
    """Клавиатура деталей курса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Записаться", callback_data=f"enroll_{course_id}")],
        [InlineKeyboardButton(text="📋 Показать уроки", callback_data=f"lessons_{course_id}")],
        [InlineKeyboardButton(text="← Назад", callback_data="courses_list")]
    ])


def get_faq_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура FAQ"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]
    ])


def get_progress_keyboard(user_courses: list) -> InlineKeyboardMarkup:
    """Клавиатура прогресса"""
    buttons = []
    for course_id in user_courses:
        if course_id in COURSES_DATA:
            course = COURSES_DATA[course_id]
            buttons.append([
                InlineKeyboardButton(
                    text=f"✏️ Обновить {course['name'][:20]}",
                    callback_data=f"progress_{course_id}_complete"
                )
            ])
    
    buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_courses_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура список курсов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]
    ])


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Пройти тест", callback_data="test_start")],
        [InlineKeyboardButton(text="📚 Все курсы", callback_data="courses_list")],
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]
    ])
