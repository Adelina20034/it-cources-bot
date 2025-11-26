# """
# Обработчики команд и callback'ов
# """
# import logging
# from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
# from aiogram.enums import ParseMode

# from app.config import COURSES_DATA, SPECIALTIES, FAQ_DATA, SPECIALTY_TEST
# from app.database import (
#     get_user, save_user, get_user_courses, 
#     add_user_course, update_user_progress
# )
# from app.keyboards import (
#     get_specialty_keyboard,
#     get_course_detail_keyboard,
#     get_specialty_keyboard_for_question,
#     get_faq_keyboard,
#     get_progress_keyboard
# )
# from app.states import TestState, CourseState, ProgressState
# from analytics.analyzer import get_courses_statistics

# logger = logging.getLogger(__name__)

# # ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

# async def get_user_progress(user_id: int, course_id: str):
#     """Получить прогресс пользователя по курсу"""
#     user = await get_user(user_id)
#     if user and 'progress' in user:
#         return user['progress'].get(course_id, {'completed': 0})
#     return {'completed': 0}

# # ============ ГЛАВНОЕ МЕНЮ ============

# async def start_command(message: Message):
#     """Команда /start"""
#     user_id = message.from_user.id
#     user_name = message.from_user.first_name
    
#     # Сохраняем/обновляем пользователя
#     user = await get_user(user_id)
#     if not user:
#         await save_user(user_id, {
#             'user_id': user_id,
#             'name': user_name,
#             'specialty': None,
#             'courses': [],
#             'progress': {}
#         })
    
#     # ✅ ГЛАВНОЕ МЕНЮ С INLINE КНОПКАМИ
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🎯 Пройти тест", callback_data="test_start")],
#             [InlineKeyboardButton(text="📚 Все курсы", callback_data="courses_list")],
#             [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule_list")],
#             [InlineKeyboardButton(text="🔍 Мои курсы", callback_data="my_courses_list")],
#             [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress_list")],
#             [InlineKeyboardButton(text="❓ FAQ", callback_data="faq_list")],
#             [InlineKeyboardButton(text="📈 Статистика", callback_data="stats_list")],
#         ]
#     )
    
#     await message.answer(
#         f"👋 Добро пожаловать, <b>{user_name}</b>!\n\n"
#         "Я помогу вам найти идеальные IT-курсы!\n\n"
#         "Выберите действие:",
#         reply_markup=keyboard
#     )

# # ============ CALLBACK HANDLERS - НАВИГАЦИЯ ============

# async def handle_test_start(callback: CallbackQuery, state: FSMContext):
#     """Начало теста"""
#     # Получаем первый вопрос
#     first_question = SPECIALTY_TEST[0] if SPECIALTY_TEST else {}
    
#     await callback.message.edit_text(
#         "🎯 <b>Тест определения специальности</b>\n\n"
#         "Я задам 7 вопросов. Выбирайте подходящий вариант.\n\n"
#         f"<b>Вопрос 1/7:</b> {first_question.get('question', 'Загрузка...')}",
#         reply_markup=get_specialty_keyboard_for_question(0)
#     )
#     await state.set_state(TestState.waiting_for_answer)
#     await state.update_data(question=0, scores={specialty: 0 for specialty in SPECIALTIES})


# async def handle_test_answer(callback: CallbackQuery, state: FSMContext):
#     """Обработка ответа в тесте"""
#     data = await state.get_data()
#     scores = data.get('scores', {})
#     question = data.get('question', 0)
    
#     # Увеличиваем счет для выбранной специальности
#     selected = callback.data.replace('test_', '')
#     if selected in scores:
#         scores[selected] += 1
    
#     question += 1
    
#     if question < 7:
#         # Получаем следующий вопрос
#         next_question = SPECIALTY_TEST[question] if question < len(SPECIALTY_TEST) else {}
        
#         await callback.message.edit_text(
#             f"<b>Вопрос {question + 1}/7:</b> {next_question.get('question', 'Загрузка...')}",
#             reply_markup=get_specialty_keyboard_for_question(question)
#         )
#         await state.update_data(question=question, scores=scores)
#     else:
#         # Определяем специальность
#         specialty = max(scores, key=scores.get)
#         user_id = callback.from_user.id
        
#         # Сохраняем специальность
#         user = await get_user(user_id)
#         if user:
#             user['specialty'] = specialty
#             await save_user(user_id, user)
        
#         # Показываем результат теста
#         back_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[[InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_main")]]
#         )
        
#         await callback.message.edit_text(
#             f"✅ <b>Ваша специальность:</b> <b>{SPECIALTIES[specialty]}</b>\n\n"
#             f"Теперь посмотрите наши курсы в каталоге!",
#             reply_markup=back_keyboard
#         )
#         await state.clear()


# async def handle_courses_list(callback: CallbackQuery):
#     """Список всех курсов"""
#     courses_text = "📚 <b>Все доступные курсы:</b>\n\n"
#     buttons = []
    
#     for course_id, course in COURSES_DATA.items():
#         courses_text += (
#             f"<b>{course['name']}</b>\n"
#             f"⏱ {course['duration_weeks']} недель | 📖 {course['lessons']} уроков\n"
#             f"💰 ${course['price']}\n\n"
#         )
#         buttons.append([InlineKeyboardButton(text=course['name'], callback_data=f"course_{course_id}")])
    
#     buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#     await callback.message.edit_text(courses_text, reply_markup=keyboard)


# async def handle_course_selection(callback: CallbackQuery):
#     """Обработка выбора курса"""
#     course_id = callback.data.replace('course_', '')
    
#     if course_id in COURSES_DATA:
#         course = COURSES_DATA[course_id]
#         text = (
#             f"<b>{course['name']}</b>\n"
#             f"{course['description']}\n\n"
#             f"⏱ Длительность: {course['duration_weeks']} недель\n"
#             f"📖 Уроков: {course['lessons']}\n"
#             f"💰 Стоимость: ${course['price']}\n"
#             f"📅 Расписание: {', '.join(course['schedule'])}\n"
#             f"Уровень: <b>{course['level']}</b>"
#         )
        
#         await callback.message.edit_text(
#             text,
#             reply_markup=get_course_detail_keyboard(course_id)
#         )


# async def handle_enroll(callback: CallbackQuery):
#     """Обработка записи на курс"""
#     course_id = callback.data.replace('enroll_', '')
#     user_id = callback.from_user.id
    
#     await add_user_course(user_id, course_id)
    
#     course = COURSES_DATA[course_id]
    
#     back_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_main")]]
#     )
    
#     await callback.message.edit_text(
#         f"✅ <b>Вы записаны на {course['name']}!</b>\n\n"
#         f"📅 Начало: {course['schedule'][0]}\n"
#         f"💬 Вы получите приглашение в группу курса.",
#         reply_markup=back_keyboard
#     )


# async def handle_schedule_list(callback: CallbackQuery):
#     """Расписание"""
#     schedule_text = "📅 <b>Расписание всех курсов:</b>\n\n"
    
#     for course_id, course in COURSES_DATA.items():
#         schedule_text += (
#             f"<b>{course['name']}</b>\n"
#             f"Время: {', '.join(course['schedule'])}\n\n"
#         )
    
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
#     )
#     await callback.message.edit_text(schedule_text, reply_markup=keyboard)


# async def handle_my_courses_list(callback: CallbackQuery):
#     """Мои курсы"""
#     user_id = callback.from_user.id
#     user_courses = await get_user_courses(user_id)
    
#     if not user_courses:
#         text = "❌ Вы пока не записаны ни на один курс.\n\nВыберите курс в каталоге."
#     else:
#         text = "📚 <b>Мои курсы:</b>\n\n"
#         for course_id in user_courses:
#             if course_id in COURSES_DATA:
#                 course = COURSES_DATA[course_id]
#                 text += f"✅ <b>{course['name']}</b>\n"
    
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
#     )
#     await callback.message.edit_text(text, reply_markup=keyboard)


# async def handle_progress_list(callback: CallbackQuery):
#     """Прогресс"""
#     user_id = callback.from_user.id
#     user_courses = await get_user_courses(user_id)
    
#     if not user_courses:
#         text = "❌ Вы не записаны ни на один курс."
#     else:
#         text = "📊 <b>Ваш прогресс:</b>\n\n"
#         for course_id in user_courses:
#             if course_id in COURSES_DATA:
#                 course = COURSES_DATA[course_id]
#                 progress_data = await get_user_progress(user_id, course_id)
#                 completed = progress_data.get('completed', 0) if progress_data else 0
#                 total = course['lessons']
#                 percentage = (completed / total * 100) if total > 0 else 0
#                 bar = '█' * int(percentage / 10) + '░' * (10 - int(percentage / 10))
                
#                 text += (
#                     f"<b>{course['name']}</b>\n"
#                     f"{bar} {percentage:.0f}%\n"
#                     f"Пройдено: {completed}/{total} уроков\n\n"
#                 )
    
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
#     )
#     await callback.message.edit_text(text, reply_markup=keyboard)


# async def handle_progress_update(callback: CallbackQuery):
#     """Обработка обновления прогресса"""
#     data = callback.data.split('_')
#     course_id = data[1]
#     action = data[2]
    
#     user_id = callback.from_user.id
    
#     if action == 'complete':
#         await update_user_progress(user_id, course_id, 1)
#         await callback.answer("✅ Урок отмечен! Отличная работа! 🎉", show_alert=True)


# async def handle_faq_list(callback: CallbackQuery):
#     """FAQ"""
#     buttons = [
#         [InlineKeyboardButton(text=faq['question'][:40] + "...", callback_data=f"faq_{faq_id}")]
#         for faq_id, faq in FAQ_DATA.items()
#     ]
#     buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])
    
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
#     await callback.message.edit_text(
#         "❓ <b>Часто задаваемые вопросы:</b>\n\n"
#         "Выберите интересующий вас вопрос:",
#         reply_markup=keyboard
#     )


# async def handle_faq_selection(callback: CallbackQuery):
#     """Обработка выбора FAQ"""
#     faq_id = callback.data.replace('faq_', '')
    
#     if faq_id in FAQ_DATA:
#         faq = FAQ_DATA[faq_id]
#         back_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[[InlineKeyboardButton(text="← Назад к FAQ", callback_data="faq_list")]]
#         )
#         await callback.message.edit_text(
#             f"<b>❓ {faq['question']}</b>\n\n"
#             f"{faq['answer']}",
#             reply_markup=back_keyboard
#         )


# async def handle_stats_list(callback: CallbackQuery):
#     """Статистика"""
#     stats = await get_courses_statistics()
    
#     text = "📊 <b>Статистика курсов:</b>\n\n"
#     text += f"Всего пользователей: {stats['total_users']}\n"
#     text += f"Всего записей: {stats['total_enrollments']}\n"
#     text += f"Средний прогресс: {stats['avg_progress']:.1f}%\n\n"
    
#     text += "<b>Популярные курсы:</b>\n"
#     for course_name, count in stats['popular_courses'].items():
#         text += f"• {course_name}: {count} студентов\n"
    
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
#     )
#     await callback.message.edit_text(text, reply_markup=keyboard)


# async def handle_back_to_main(callback: CallbackQuery):
#     """Возврат в главное меню"""
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🎯 Пройти тест", callback_data="test_start")],
#             [InlineKeyboardButton(text="📚 Все курсы", callback_data="courses_list")],
#             [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule_list")],
#             [InlineKeyboardButton(text="🔍 Мои курсы", callback_data="my_courses_list")],
#             [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress_list")],
#             [InlineKeyboardButton(text="❓ FAQ", callback_data="faq_list")],
#             [InlineKeyboardButton(text="📈 Статистика", callback_data="stats_list")],
#         ]
#     )
    
#     await callback.message.edit_text(
#         "👈 <b>Главное меню</b>\n\n"
#         "Выберите действие:",
#         reply_markup=keyboard
#     )


# ============ HANDLERS.PY ============

"""
Обработчики команд и callback'ов
"""
import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.config import COURSES_DATA, SPECIALTIES, FAQ_DATA, SPECIALTY_TEST
from app.database import (
    get_user, save_user, get_user_courses, 
    add_user_course, update_user_progress
)
from app.keyboards import (
    get_specialty_keyboard,
    get_course_detail_keyboard,
    get_specialty_keyboard_for_question,
    get_faq_keyboard,
    get_progress_keyboard,
    get_my_courses_keyboard,
    get_my_course_detail_keyboard,
    get_my_lessons_keyboard,
    get_lesson_mark_keyboard
)
from app.states import TestState
from analytics.analyzer import get_courses_statistics

logger = logging.getLogger(__name__)


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

async def get_user_progress(user_id: int, course_id: str):
    """Получить прогресс пользователя по курсу"""
    user = await get_user(user_id)
    if user and 'progress' in user:
        return user['progress'].get(course_id, {'completed': 0})
    return {'completed': 0}


# ============ ГЛАВНОЕ МЕНЮ ============

async def start_command(message: Message):
    """Команда /start"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    user = await get_user(user_id)
    if not user:
        await save_user(user_id, {
            'user_id': user_id,
            'name': user_name,
            'specialty': None,
            'courses': [],
            'progress': {}
        })
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Пройти тест", callback_data="test_start")],
            [InlineKeyboardButton(text="📚 Все курсы", callback_data="courses_list")],
            [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule_list")],
            [InlineKeyboardButton(text="🔍 Мои курсы", callback_data="my_courses_list")],
            [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress_list")],
            [InlineKeyboardButton(text="❓ FAQ", callback_data="faq_list")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="stats_list")],
        ]
    )
    
    await message.answer(
        f"👋 Добро пожаловать, <b>{user_name}</b>!\n\n"
        "Я помогу вам найти идеальные IT-курсы!\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


# ============ CALLBACK HANDLERS - ТЕСТ ============

async def handle_test_start(callback: CallbackQuery, state: FSMContext):
    """Начало теста"""
    first_question = SPECIALTY_TEST[0] if SPECIALTY_TEST else {}
    
    await callback.message.edit_text(
        "🎯 <b>Тест определения специальности</b>\n\n"
        "Я задам 7 вопросов. Выбирайте подходящий вариант.\n\n"
        f"<b>Вопрос 1/7:</b> {first_question.get('question', 'Загрузка...')}",
        reply_markup=get_specialty_keyboard_for_question(0)
    )
    await state.set_state(TestState.waiting_for_answer)
    await state.update_data(question=0, scores={specialty: 0 for specialty in SPECIALTIES})


async def handle_test_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа в тесте"""
    data = await state.get_data()
    scores = data.get('scores', {})
    question = data.get('question', 0)
    
    selected = callback.data.replace('test_', '')
    if selected in scores:
        scores[selected] += 1
    
    question += 1
    
    if question < 7:
        next_question = SPECIALTY_TEST[question] if question < len(SPECIALTY_TEST) else {}
        
        await callback.message.edit_text(
            f"<b>Вопрос {question + 1}/7:</b> {next_question.get('question', 'Загрузка...')}",
            reply_markup=get_specialty_keyboard_for_question(question)
        )
        await state.update_data(question=question, scores=scores)
    else:
        specialty = max(scores, key=scores.get)
        user_id = callback.from_user.id
        
        user = await get_user(user_id)
        if user:
            user['specialty'] = specialty
            await save_user(user_id, user)
        
        back_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_main")]]
        )
        
        await callback.message.edit_text(
            f"✅ <b>Ваша специальность:</b> <b>{SPECIALTIES[specialty]}</b>\n\n"
            f"Теперь посмотрите наши курсы в каталоге!",
            reply_markup=back_keyboard
        )
        await state.clear()


# ============ CALLBACK HANDLERS - КУРСЫ ============

async def handle_courses_list(callback: CallbackQuery):
    """Список всех курсов"""
    courses_text = "📚 <b>Все доступные курсы:</b>\n\n"
    buttons = []
    
    for course_id, course in COURSES_DATA.items():
        courses_text += (
            f"<b>{course['name']}</b>\n"
            f"⏱ {course['duration_weeks']} недель | 📖 {course['lessons']} уроков\n"
            f"💰 ${course['price']}\n\n"
        )
        buttons.append([InlineKeyboardButton(text=course['name'], callback_data=f"course_{course_id}")])
    
    buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(courses_text, reply_markup=keyboard)


async def handle_course_selection(callback: CallbackQuery):
    """Обработка выбора курса"""
    course_id = callback.data.replace('course_', '')
    
    if course_id in COURSES_DATA:
        course = COURSES_DATA[course_id]
        text = (
            f"<b>{course['name']}</b>\n"
            f"{course['description']}\n\n"
            f"⏱ Длительность: {course['duration_weeks']} недель\n"
            f"📖 Уроков: {course['lessons']}\n"
            f"💰 Стоимость: ${course['price']}\n"
            f"📅 Расписание: {', '.join(course['schedule'])}\n"
            f"Уровень: <b>{course['level']}</b>"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_course_detail_keyboard(course_id)
        )


async def handle_enroll(callback: CallbackQuery):
    """Обработка записи на курс"""
    course_id = callback.data.replace('enroll_', '')
    user_id = callback.from_user.id
    
    await add_user_course(user_id, course_id)
    
    course = COURSES_DATA[course_id]
    
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="← Назад в меню", callback_data="back_to_main")]]
    )
    
    await callback.message.edit_text(
        f"✅ <b>Вы записаны на {course['name']}!</b>\n\n"
        f"📅 Начало: {course['schedule'][0]}\n"
        f"💬 Вы получите приглашение в группу курса.",
        reply_markup=back_keyboard
    )


# ============ CALLBACK HANDLERS - МОИ КУРСЫ ============

async def handle_my_courses_list(callback: CallbackQuery):
    """Мои курсы"""
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if not user_courses:
        text = "❌ Вы пока не записаны ни на один курс.\n\nВыберите курс в каталоге."
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
        )
    else:
        text = "📚 <b>Мои курсы:</b>\n\n"
        for course_id in user_courses:
            if course_id in COURSES_DATA:
                course = COURSES_DATA[course_id]
                user = await get_user(user_id)
                progress = user.get('progress', {}).get(course_id, {}) if user else {}
                completed = progress.get('completed', 0)
                percentage = (completed / course['lessons'] * 100) if course['lessons'] > 0 else 0
                
                text += (
                    f"✅ <b>{course['name']}</b>\n"
                    f"Прогресс: {completed}/{course['lessons']} уроков ({percentage:.0f}%)\n\n"
                )
        
        keyboard = get_my_courses_keyboard(user_courses)
    
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_my_course_detail(callback: CallbackQuery):
    """Детали моего курса"""
    course_id = callback.data.replace('my_course_', '')
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if course_id not in user_courses:
        await callback.answer("❌ Вы не записаны на этот курс!", show_alert=True)
        return
    
    if course_id not in COURSES_DATA:
        await callback.answer("❌ Курс не найден", show_alert=True)
        return
    
    course = COURSES_DATA[course_id]
    
    user = await get_user(user_id)
    progress = user.get('progress', {}).get(course_id, {}) if user else {}
    completed = progress.get('completed', 0)
    percentage = (completed / course['lessons'] * 100) if course['lessons'] > 0 else 0
    bar = '█' * int(percentage / 10) + '░' * (10 - int(percentage / 10))
    
    text = (
        f"<b>📚 {course['name']}</b>\n\n"
        f"📊 Прогресс: {completed}/{course['lessons']} уроков\n"
        f"{bar} {percentage:.0f}%\n\n"
        f"⏱ Длительность: {course['duration_weeks']} недель\n"
        f"📅 Расписание: {', '.join(course['schedule'])}"
    )
    
    keyboard = get_my_course_detail_keyboard(course_id)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_my_lessons(callback: CallbackQuery):
    """Показать уроки моего курса для отмечания прогресса"""
    course_id = callback.data.replace('my_lessons_', '')
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if course_id not in user_courses:
        await callback.answer("❌ Вы не записаны на этот курс!", show_alert=True)
        return
    
    if course_id not in COURSES_DATA:
        await callback.answer("❌ Курс не найден", show_alert=True)
        return
    
    course = COURSES_DATA[course_id]
    lessons = course.get('lessons_list', [])
    
    user = await get_user(user_id)
    progress = user.get('progress', {}).get(course_id, {}) if user else {}
    completed = progress.get('completed', 0)
    
    text = f"<b>📖 {course['name']}</b>\n\n"
    text += f"Пройдено: {completed}/{len(lessons)} уроков\n\n"
    text += "<b>Список уроков:</b>\n\n"
    
    for i, lesson in enumerate(lessons, 1):
        status = "✅" if i <= completed else "⭕"
        text += f"{status} {i}. {lesson}\n"
    
    keyboard = get_my_lessons_keyboard(course_id)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_mark_progress(callback: CallbackQuery):
    """Показать урок для отмечания"""
    # data = callback.data.split('_')
    # course_id = data[2]
    # lesson_index = int(data[3])4

    parts = callback.data.split('_')
    lesson_index = int(parts[-1])  # Последний элемент - индекс
    course_id = '_'.join(parts[2:-1])  # Все между mark_progress и индексом
    
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if course_id not in user_courses:
        await callback.answer("❌ Вы не записаны на этот курс!", show_alert=True)
        return
    
    if course_id not in COURSES_DATA:
        await callback.answer("❌ Курс не найден", show_alert=True)
        return
    
    course = COURSES_DATA[course_id]
    lessons = course.get('lessons_list', [])
    
    if lesson_index >= len(lessons):
        await callback.answer("❌ Урок не найден", show_alert=True)
        return
    
    lesson_name = lessons[lesson_index]
    
    user = await get_user(user_id)
    progress = user.get('progress', {}).get(course_id, {}) if user else {}
    completed = progress.get('completed', 0)
    is_completed = lesson_index < completed
    
    text = (
        f"<b>📖 {course['name']}</b>\n\n"
        f"<b>Урок {lesson_index + 1}:</b> {lesson_name}\n\n"
        f"Статус: {'✅ Пройден' if is_completed else '⭕ Не пройден'}"
    )
    
    keyboard = get_lesson_mark_keyboard(course_id, lesson_index)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_complete_progress(callback: CallbackQuery):
    """Отметить урок как пройденный"""
    # data = callback.data.split('_')
    # course_id = data[2]
    # lesson_index = int(data[3])
    parts = callback.data.split('_')
    lesson_index = int(parts[-1])  # Последний элемент - индекс
    course_id = '_'.join(parts[2:-1])  # Все между complete_progress и индексом
    
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if course_id not in user_courses:
        await callback.answer("❌ Вы не записаны на этот курс!", show_alert=True)
        return
    
    user = await get_user(user_id)
    if user:
        if course_id not in user['progress']:
            user['progress'][course_id] = {'completed': 0}
        
        user['progress'][course_id]['completed'] = lesson_index + 1
        await save_user(user_id, user)
    
    course = COURSES_DATA[course_id]
    lessons = course.get('lessons_list', [])
    completed = lesson_index + 1
    percentage = (completed / len(lessons) * 100) if len(lessons) > 0 else 0
    bar = '█' * int(percentage / 10) + '░' * (10 - int(percentage / 10))
    
    text = (
        f"✅ <b>Урок отмечен!</b>\n\n"
        f"<b>{course['name']}</b>\n"
        f"Прогресс: {completed}/{len(lessons)} уроков\n"
        f"{bar} {percentage:.0f}%"
    )
    
    await callback.answer("✅ Отличная работа! 🎉", show_alert=True)
    
    keyboard = get_my_lessons_keyboard(course_id)
    await callback.message.edit_text(text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - РАСПИСАНИЕ ============

async def handle_schedule_list(callback: CallbackQuery):
    """Расписание"""
    schedule_text = "📅 <b>Расписание всех курсов:</b>\n\n"
    
    for course_id, course in COURSES_DATA.items():
        schedule_text += (
            f"<b>{course['name']}</b>\n"
            f"Время: {', '.join(course['schedule'])}\n\n"
        )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
    )
    await callback.message.edit_text(schedule_text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - ПРОГРЕСС ============

async def handle_progress_list(callback: CallbackQuery):
    """Прогресс"""
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if not user_courses:
        text = "❌ Вы не записаны ни на один курс."
    else:
        text = "📊 <b>Ваш прогресс:</b>\n\n"
        for course_id in user_courses:
            if course_id in COURSES_DATA:
                course = COURSES_DATA[course_id]
                progress_data = await get_user_progress(user_id, course_id)
                completed = progress_data.get('completed', 0) if progress_data else 0
                total = course['lessons']
                percentage = (completed / total * 100) if total > 0 else 0
                bar = '█' * int(percentage / 10) + '░' * (10 - int(percentage / 10))
                
                text += (
                    f"<b>{course['name']}</b>\n"
                    f"{bar} {percentage:.0f}%\n"
                    f"Пройдено: {completed}/{total} уроков\n\n"
                )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
    )
    await callback.message.edit_text(text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - FAQ ============

async def handle_faq_list(callback: CallbackQuery):
    """FAQ"""
    buttons = [
        [InlineKeyboardButton(text=faq['question'][:40] + "...", callback_data=f"faq_{faq_id}")]
        for faq_id, faq in FAQ_DATA.items()
    ]
    buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        "❓ <b>Часто задаваемые вопросы:</b>\n\n"
        "Выберите интересующий вас вопрос:",
        reply_markup=keyboard
    )


async def handle_faq_selection(callback: CallbackQuery):
    """Обработка выбора FAQ"""
    faq_id = callback.data.replace('faq_', '')
    
    if faq_id in FAQ_DATA:
        faq = FAQ_DATA[faq_id]
        back_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="← Назад к FAQ", callback_data="faq_list")]]
        )
        await callback.message.edit_text(
            f"<b>❓ {faq['question']}</b>\n\n"
            f"{faq['answer']}",
            reply_markup=back_keyboard
        )


# ============ CALLBACK HANDLERS - СТАТИСТИКА ============

async def handle_stats_list(callback: CallbackQuery):
    """Статистика"""
    stats = await get_courses_statistics()
    
    text = "📊 <b>Статистика курсов:</b>\n\n"
    text += f"Всего пользователей: {stats['total_users']}\n"
    text += f"Всего записей: {stats['total_enrollments']}\n"
    text += f"Средний прогресс: {stats['avg_progress']:.1f}%\n\n"
    
    text += "<b>Популярные курсы:</b>\n"
    for course_name, count in stats['popular_courses'].items():
        text += f"• {course_name}: {count} студентов\n"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="back_to_main")]]
    )
    await callback.message.edit_text(text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - НАВИГАЦИЯ ============

async def handle_back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Пройти тест", callback_data="test_start")],
            [InlineKeyboardButton(text="📚 Все курсы", callback_data="courses_list")],
            [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule_list")],
            [InlineKeyboardButton(text="🔍 Мои курсы", callback_data="my_courses_list")],
            [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress_list")],
            [InlineKeyboardButton(text="❓ FAQ", callback_data="faq_list")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="stats_list")],
        ]
    )
    
    await callback.message.edit_text(
        "👈 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
