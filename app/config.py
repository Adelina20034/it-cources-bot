"""
Конфигурация и константы приложения
Загрузка данных из JSON файлов
"""
import os
import json
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

# ============ TELEGRAM BOT CONFIGURATION ============
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0)) 

# # ============ APPLICATION SETTINGS ============
# DEBUG = os.getenv('DEBUG', 'False') == 'True'
# WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://yourdomain.com')
# WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8443))

# ============ DATABASE PATHS ============
DATA_DIR = 'data'
SPECIALTIES_FILE = os.path.join(DATA_DIR, 'specialties.json')
COURSES_FILE = os.path.join(DATA_DIR, 'courses.json')
TEST_FILE = os.path.join(DATA_DIR, 'test.json')
FAQ_FILE = os.path.join(DATA_DIR, 'faq.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Создаем директорию data если её нет
os.makedirs(DATA_DIR, exist_ok=True)

# ============ ФУНКЦИИ ЗАГРУЗКИ JSON ============

def load_json(filepath: str, default: any = None) -> any:
    """
    Загрузить JSON файл
    
    Args:
        filepath: Путь к файлу
        default: Значение по умолчанию если файл не найден
    
    Returns:
        Данные из JSON или значение по умолчанию
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Загружен {filepath}")
            return data
    except FileNotFoundError:
        print(f"⚠️ Файл {filepath} не найден!")
        return default if default is not None else {}
    except json.JSONDecodeError:
        print(f"❌ Ошибка при чтении JSON: {filepath}")
        return default if default is not None else {}

# ============ ЗАГРУЗКА ДАННЫХ ИЗ JSON ============

# Специальности
SPECIALTIES: Dict[str, str] = load_json(SPECIALTIES_FILE, {})

# Курсы
COURSES_DATA: Dict[str, Dict] = load_json(COURSES_FILE, {})

# Тест для определения специальности
SPECIALTY_TEST: List[Dict] = load_json(TEST_FILE, [])

# FAQ
FAQ_DATA: Dict[str, Dict] = load_json(FAQ_FILE, {})

# ============ ПРОВЕРКА ЗАГРУЖЕННЫХ ДАННЫХ ============

if not SPECIALTIES:
    print("⚠️ Специальности не загружены!")
    
if not COURSES_DATA:
    print("⚠️ Курсы не загружены!")
    
if not SPECIALTY_TEST:
    print("⚠️ Тест не загружен!")
    
if not FAQ_DATA:
    print("⚠️ FAQ не загружены!")

# ============ СООБЩЕНИЯ ============

MESSAGES = {
    'welcome': """
👋 Добро пожаловать в IT-Курсы!

Давайте начнём с небольшого теста, чтобы определить вашу специальность!
    """,
    
    'test_intro': "🎯 <b>Тест определения специальности</b>\n\nЯ задам 7 вопросов. Выбирайте подходящий вариант.",
    
    'test_result': "✅ <b>Ваша специальность:</b> <b>{specialty}</b>\n\nТеперь посмотрите наши курсы в каталоге!",
    
    'courses_header': "📚 <b>Все доступные курсы:</b>\n\n",
    'course_info': "<b>{name}</b>\n⏱ {duration_weeks} недель | 📖 {lessons} уроков\n💰 ${price}\n\n",
    
    'course_detail': "<b>{name}</b>\n{description}\n\n⏱ Длительность: {duration_weeks} недель\n📖 Уроков: {lessons}\n💰 Стоимость: ${price}\n📅 Расписание: {schedule}\nУровень: <b>{level}</b>",
    
    'enrolled_success': "✅ <b>Вы записаны на {course_name}!</b>\n\n📅 Начало: {start_date}\n💬 Вы получите приглашение в группу курса.",
    
    'my_courses_empty': "❌ Вы пока не записаны ни на один курс.\n\nВыберите курс в каталоге.",
    'my_courses_header': "📚 <b>Мои курсы:</b>\n\n",
    'my_course_item': "✅ <b>{name}</b>\nПрогресс: {completed}/{total} уроков ({percentage:.0f}%)\n\n",
    
    'course_detail_header': "<b>📚 {name}</b>\n\n📊 Прогресс: {completed}/{total} уроков\n{progress_bar} {percentage:.0f}%\n\n⏱ Длительность: {duration_weeks} недель\n📅 Расписание: {schedule}",
    
    'lessons_header': "<b>📖 {course_name}</b>\n\nПройдено: {completed}/{total} уроков\n\n<b>Список уроков:</b>\n\n",
    'lesson_item': "{status} {number}. {name}\n",
    
    'lesson_detail': "<b>📖 {course_name}</b>\n\n<b>Урок {lesson_number}:</b> {lesson_name}\n\nСтатус: {status}",
    'lesson_completed': "✅ <b>Урок отмечен!</b>\n\n<b>{course_name}</b>\nПрогресс: {completed}/{total} уроков\n{progress_bar} {percentage:.0f}%",
    
    'schedule_header': "📅 <b>Расписание всех курсов:</b>\n\n",
    'schedule_item': "<b>{name}</b>\nВремя: {schedule}\n\n",
    
    'progress_header': "📊 <b>Ваш прогресс:</b>\n\n",
    'progress_item': "<b>{name}</b>\n{progress_bar} {percentage:.0f}%\nПройдено: {completed}/{total} уроков\n\n",
    'progress_empty': "❌ Вы не записаны ни на один курс.",
    
    'faq_header': "❓ <b>Часто задаваемые вопросы:</b>\n\nВыберите интересующий вас вопрос:",
    'faq_detail': "<b>❓ {question}</b>\n\n{answer}",
    
    'stats_header': "📊 <b>Статистика курсов:</b>\n\n",
    'stats_content': "Всего пользователей: {total_users}\nВсего записей: {total_enrollments}\nСредний прогресс: {avg_progress:.1f}%\n\n<b>Популярные курсы:</b>\n",
    'stats_course': "• {name}: {count} студентов\n",
    
    'main_menu': "<b>Главное меню</b>\n\nВыберите действие:",
    
    'error_not_enrolled': "❌ Вы не записаны на этот курс!",
    'error_course_not_found': "❌ Курс не найден",
    'error_lesson_not_found': "❌ Урок не найден",
    
    'success_alert': "✅ Отличная работа! 🎉",
}

print("✅ Config загружен успешно!")
