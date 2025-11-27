"""
Клавиатуры и меню для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import SPECIALTY_TEST, COURSES_DATA

def get_specialty_keyboard_for_question(question_index: int) -> InlineKeyboardMarkup:
    """
    Получить клавиатуру для конкретного вопроса теста
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
        [InlineKeyboardButton(text="← Назад", callback_data="courses_list")]
    ])


def get_my_courses_keyboard(user_courses: list) -> InlineKeyboardMarkup:
    """Клавиатура списка моих курсов"""
    buttons = []
    for course_id in user_courses:
        if course_id in COURSES_DATA:
            course = COURSES_DATA[course_id]
            buttons.append([
                InlineKeyboardButton(text=f"📚 {course['name']}", callback_data=f"my_course_{course_id}")
            ])
    buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_my_course_detail_keyboard(course_id: str) -> InlineKeyboardMarkup:
    """Клавиатура деталей моего курса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Показать уроки", callback_data=f"my_lessons_{course_id}")],
        [InlineKeyboardButton(text="← Назад к моим курсам", callback_data="my_courses_list")]
    ])


def get_my_lessons_keyboard(course_id: str) -> InlineKeyboardMarkup:
    """Клавиатура уроков моего курса для отмечания прогресса"""
    buttons = []
    if course_id in COURSES_DATA:
        course = COURSES_DATA[course_id]
        lessons = course.get('lessons_list', [])
        for i, lesson in enumerate(lessons, 1):
            buttons.append([
                InlineKeyboardButton(
                    text=f"Урок {i}: {lesson[:35]}", 
                    callback_data=f"mark_progress_{course_id}_{i-1}"
                )
            ])
    buttons.append([InlineKeyboardButton(text="← Назад", callback_data=f"my_course_{course_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_mark_keyboard(course_id: str, lesson_index: int) -> InlineKeyboardMarkup:
    """Клавиатура для отмечания урока"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отметить как пройденный", callback_data=f"complete_progress_{course_id}_{lesson_index}")],
        [InlineKeyboardButton(text="← Назад", callback_data=f"my_lessons_{course_id}")]
    ])