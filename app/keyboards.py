"""
Клавиатуры и меню для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import FAQ_DATA, SPECIALTY_TEST, COURSES_DATA


def get_main_keyboard(user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Главное меню бота с проверкой прав доступа
    """
    from app.config import ADMIN_ID
    
    buttons = [
        [InlineKeyboardButton(text="🎯 Пройти тест", callback_data="test_start")],
        [InlineKeyboardButton(text="📚 Все курсы", callback_data="courses_list")],
        [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule_list")],
        [InlineKeyboardButton(text="🔍 Мои курсы", callback_data="my_courses_list")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress_list")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq_list")],
    ]
    
    # Кнопка статистики только для админа
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton(text="📈 Статистика", callback_data="stats_list")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
    back_button = get_back_to_main_keyboard().inline_keyboard[0]
    buttons.append(back_button)
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


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """
    Простая клавиатура с кнопкой "Назад в меню"

    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_main")]
        ]
    )

def get_courses_list_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура со списком всех доступных курсов
    """
    buttons = []
    
    for course_id, course in COURSES_DATA.items():
        buttons.append([
            InlineKeyboardButton(
                text=course['name'],
                callback_data=f"course_{course_id}"
            )
        ])
    
    back_button = get_back_to_main_keyboard().inline_keyboard[0]
    buttons.append(back_button)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_list_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура со списком вопросов FAQ

    """
    buttons = [
        [InlineKeyboardButton(
            text=faq['question'][:40] + "...",
            callback_data=f"faq_{faq_id}"
        )]
        for faq_id, faq in FAQ_DATA.items()
    ]

    back_button = get_back_to_main_keyboard().inline_keyboard[0]
    buttons.append(back_button)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_detail_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для детального просмотра FAQ
    
    Returns:
        InlineKeyboardMarkup с кнопкой "Назад к FAQ"
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="← Назад к FAQ", callback_data="faq_list")]
        ]
    )