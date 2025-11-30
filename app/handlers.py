"""
Обработчики команд и callback'ов
"""
import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.config import COURSES_DATA, SPECIALTIES, FAQ_DATA, SPECIALTY_TEST, MESSAGES
from app.database import (
    get_user, save_user, get_user_courses, 
    add_user_course
)
from app.keyboards import (
    get_course_detail_keyboard,
    get_specialty_keyboard_for_question,
    get_my_courses_keyboard,
    get_my_course_detail_keyboard,
    get_my_lessons_keyboard,
    get_lesson_mark_keyboard,
    get_main_keyboard,
    get_back_to_main_keyboard,
    get_courses_list_keyboard,
    get_faq_list_keyboard,
    get_faq_detail_keyboard
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
    
    # ✨ ИЗМЕНЕНО: Используем функцию get_main_keyboard
    keyboard = get_main_keyboard(user_id)
    
    await message.answer(
        MESSAGES['welcome'].format(name=user_name),
        reply_markup=keyboard
    )


# ============ CALLBACK HANDLERS - ТЕСТ ============

async def handle_test_start(callback: CallbackQuery, state: FSMContext):
    """Начало теста"""
    first_question = SPECIALTY_TEST[0] if SPECIALTY_TEST else {}
    
    question_text = MESSAGES['test_intro'] + f"\n\n<b>Вопрос 1/7:</b> {first_question.get('question', 'Загрузка...')}"
    
    await callback.message.edit_text(
        question_text,
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
        
        back_keyboard = get_back_to_main_keyboard()

        
        await callback.message.edit_text(
            MESSAGES['test_result'].format(specialty=SPECIALTIES[specialty]),
            reply_markup=back_keyboard
        )
        await state.clear()


# ============ CALLBACK HANDLERS - КУРСЫ ============

async def handle_courses_list(callback: CallbackQuery):
    """Список всех курсов"""
    courses_text = MESSAGES['courses_header']
    
    for course_id, course in COURSES_DATA.items():
        courses_text += MESSAGES['course_info'].format(
            name=course['name'],
            duration_weeks=course['duration_weeks'],
            lessons=course['lessons'],
            price=course['price']
        )
    
    keyboard = get_courses_list_keyboard()
    
    await callback.message.edit_text(courses_text, reply_markup=keyboard)


async def handle_course_selection(callback: CallbackQuery):
    """Обработка выбора курса"""
    course_id = callback.data.replace('course_', '')
    
    if course_id in COURSES_DATA:
        course = COURSES_DATA[course_id]
        text = MESSAGES['course_detail'].format(
            name=course['name'],
            description=course['description'],
            duration_weeks=course['duration_weeks'],
            lessons=course['lessons'],
            price=course['price'],
            schedule=', '.join(course['schedule']),
            level=course['level']
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
    
    back_keyboard = get_back_to_main_keyboard()

    await callback.message.edit_text(
        MESSAGES['enrolled_success'].format(
            course_name=course['name'],
            start_date=course['schedule'][0]
        ),
        reply_markup=back_keyboard
    )


# ============ CALLBACK HANDLERS - РАСПИСАНИЕ ============

async def handle_schedule_list(callback: CallbackQuery):
    """Расписание"""
    schedule_text = MESSAGES['schedule_header']
    
    for course_id, course in COURSES_DATA.items():
        schedule_text += (
            MESSAGES['schedule_item'].format(
                    name=course['name'],
                    schedule=course['schedule']
                )
        )
    
    keyboard = get_back_to_main_keyboard()

    await callback.message.edit_text(schedule_text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - МОИ КУРСЫ ============

async def handle_my_courses_list(callback: CallbackQuery):
    """Мои курсы"""
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if not user_courses:
        text = MESSAGES['my_courses_empty']
        keyboard = get_back_to_main_keyboard()
    else:
        text = MESSAGES['my_courses_header']
        for course_id in user_courses:
            if course_id in COURSES_DATA:
                course = COURSES_DATA[course_id]
                user = await get_user(user_id)
                progress = user.get('progress', {}).get(course_id, {}) if user else {}
                completed = progress.get('completed', 0)
                percentage = (completed / course['lessons'] * 100) if course['lessons'] > 0 else 0
                
                text += MESSAGES['my_course_item'].format(
                    name=course['name'],
                    completed=completed,
                    total=course['lessons'],
                    percentage=percentage
                )
        
        keyboard = get_my_courses_keyboard(user_courses)
    
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_my_course_detail(callback: CallbackQuery):
    """Детали моего курса"""
    course_id = callback.data.replace('my_course_', '')
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    # if course_id not in user_courses:
    #     await callback.answer(MESSAGES['error_not_enrolled'], show_alert=True)
    #     return
    
    if course_id not in COURSES_DATA:
        await callback.answer(MESSAGES['error_course_not_found'], show_alert=True)
        return
    
    course = COURSES_DATA[course_id]
    
    user = await get_user(user_id)
    progress = user.get('progress', {}).get(course_id, {}) if user else {}
    completed = progress.get('completed', 0)
    percentage = (completed / course['lessons'] * 100) if course['lessons'] > 0 else 0
    bar = '█' * int(percentage / 10) + '░' * (10 - int(percentage / 10))
    
    text = MESSAGES['course_detail_header'].format(
            name=course['name'],
            completed=completed,
            total=course['lessons'],
            progress_bar=bar,
            percentage=percentage,
            duration_weeks=course['duration_weeks'],
            schedule=course['schedule']
        )

    keyboard = get_my_course_detail_keyboard(course_id)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_my_lessons(callback: CallbackQuery):
    """Показать уроки моего курса для отмечания прогресса"""
    course_id = callback.data.replace('my_lessons_', '')
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    # if course_id not in user_courses:
    #     await callback.answer(MESSAGES['error_not_enrolled'], show_alert=True)
    #     return
    
    if course_id not in COURSES_DATA:
        await callback.answer(MESSAGES['error_course_not_found'], show_alert=True)
        return
    
    course = COURSES_DATA[course_id]
    lessons = course.get('lessons_list', [])
    
    user = await get_user(user_id)
    progress = user.get('progress', {}).get(course_id, {}) if user else {}
    completed = progress.get('completed', 0)
    
    text = MESSAGES['lessons_header'].format(
                    course_name=course['name'],
                    completed=completed,
                    total=len(lessons),
                )
    
    for i, lesson in enumerate(lessons, 1):
        status = "✅" if i <= completed else "⭕"
        text += MESSAGES['lesson_item'].format(
                    status=status,
                    number=i,
                    name=lesson
                )
    
    keyboard = get_my_lessons_keyboard(course_id)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_mark_progress(callback: CallbackQuery):
    """Показать урок для отмечания"""
    
    parts = callback.data.split('_')
    lesson_index = int(parts[-1])  # Последний элемент - индекс
    course_id = '_'.join(parts[2:-1])  # Все между mark_progress и индексом
    
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    # if course_id not in user_courses:
    #     await callback.answer(MESSAGES['error_not_enrolled'], show_alert=True)
    #     return
    
    if course_id not in COURSES_DATA:
        await callback.answer(MESSAGES['error_course_not_found'], show_alert=True)
        return
    
    course = COURSES_DATA[course_id]
    lessons = course.get('lessons_list', [])
    
    if lesson_index >= len(lessons):
        await callback.answer(MESSAGES['error_lesson_not_found'], show_alert=True)
        return
    
    lesson_name = lessons[lesson_index]
    
    user = await get_user(user_id)
    progress = user.get('progress', {}).get(course_id, {}) if user else {}
    completed = progress.get('completed', 0)
    is_completed = lesson_index < completed

    text = MESSAGES['lesson_detail'].format(
        course_name=course['name'],
        lesson_number=lesson_index + 1,
        lesson_name=lesson_name,
        status='✅ Пройден' if is_completed else '⭕ Не пройден'
    )
    
    keyboard = get_lesson_mark_keyboard(course_id, lesson_index)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_complete_progress(callback: CallbackQuery):
    """Отметить урок как пройденный"""

    parts = callback.data.split('_')
    lesson_index = int(parts[-1])  # Последний элемент - индекс
    course_id = '_'.join(parts[2:-1])  # Все между complete_progress и индексом
    
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    # if course_id not in user_courses:
    #     await callback.answer(MESSAGES['error_not_enrolled'], show_alert=True)
    #     return
    
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
    
    text = MESSAGES['lesson_completed'].format(
        course_name=course['name'],
        completed=completed,
        total=len(lessons),
        progress_bar=bar,
        percentage=percentage
        )
    
    
    await callback.answer(MESSAGES['success_alert'], show_alert=True)
    
    keyboard = get_my_lessons_keyboard(course_id)
    await callback.message.edit_text(text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - ПРОГРЕСС ============

async def handle_progress_list(callback: CallbackQuery):
    """Прогресс"""
    user_id = callback.from_user.id
    user_courses = await get_user_courses(user_id)
    
    if not user_courses:
        text = MESSAGES['progress_empty']
    else:
        text = MESSAGES['progress_header']
        for course_id in user_courses:
            if course_id in COURSES_DATA:
                course = COURSES_DATA[course_id]
                progress_data = await get_user_progress(user_id, course_id)
                completed = progress_data.get('completed', 0) if progress_data else 0
                total = course['lessons']
                percentage = (completed / total * 100) if total > 0 else 0
                bar = '█' * int(percentage / 10) + '░' * (10 - int(percentage / 10))
                
                text += MESSAGES['progress_item'].format(
                    name=course['name'],
                    progress_bar=bar,
                    percentage=percentage,
                    completed=completed,
                    total=total
                )
    
    keyboard = get_back_to_main_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard)


# ============ CALLBACK HANDLERS - FAQ ============

async def handle_faq_list(callback: CallbackQuery):
    """FAQ"""

    keyboard = get_faq_list_keyboard()
    
    await callback.message.edit_text(
        MESSAGES['faq_header'],
        reply_markup=keyboard
    )


async def handle_faq_selection(callback: CallbackQuery):
    """Обработка выбора FAQ"""
    faq_id = callback.data.replace('faq_', '')
    
    if faq_id in FAQ_DATA:
        faq = FAQ_DATA[faq_id]
        back_keyboard = get_faq_detail_keyboard()

        await callback.message.edit_text(
            MESSAGES['faq_detail'].format(
                question=faq['question'],
                answer=faq['answer']                
            ),
            reply_markup=back_keyboard
        )

# ============ CALLBACK HANDLERS - СТАТИСТИКА ============

async def handle_stats_list(callback: CallbackQuery):
    """Статистика курсов с графиками"""
    from analytics.analyzer import generate_statistics_chart
    from aiogram.types import BufferedInputFile
    
    # from app.config import ADMIN_ID
    
    # if callback.from_user.id != ADMIN_ID:
    #     await callback.answer(
    #         "❌ Доступ запрещён! Статистика доступна только администратору.",
    #         show_alert=True
    #     )
    #     return

    # Получаем статистику
    stats = await get_courses_statistics()
    
    # Формируем текст
    text = MESSAGES['stats_header']
    text += MESSAGES['stats_content'].format(
        total_users=stats['total_users'],
        total_enrollments=stats['total_enrollments'],
        avg_progress=stats['avg_progress']
    )
    
    for course_name, count in stats['popular_courses'].items():
        text += MESSAGES['stats_course'].format(name=course_name, count=count)
    
    keyboard = get_back_to_main_keyboard()
    
    # Генерируем график
    chart_buffer = await generate_statistics_chart(stats)
    
    if chart_buffer:
        # Если есть данные для графика — отправляем фото с текстом
        photo = BufferedInputFile(chart_buffer.getvalue(), filename="stats.png")
        
        await callback.answer()
        
        # Отправляем фото с текстом статистики
        await callback.message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=keyboard
        )
    else:
        # Если нет данных для графика — просто текст
        await callback.message.edit_text(text, reply_markup=keyboard)

# ============ CALLBACK HANDLERS - НАВИГАЦИЯ ============

async def handle_back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    keyboard = get_main_keyboard(callback.from_user.id)
    
    # Проверяем, есть ли текст в сообщении
    if callback.message.text:
        # Если это текстовое сообщение — редактируем
        await callback.message.edit_text(
            MESSAGES['main_menu'],
            reply_markup=keyboard
        )
    else:
        # Если это фото/видео/файл — удаляем
        await callback.message.delete()
