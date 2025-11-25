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
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

# ============ APPLICATION SETTINGS ============
DEBUG = os.getenv('DEBUG', 'False') == 'True'
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://yourdomain.com')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8443))

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
SPECIALTIES: Dict[str, str] = load_json(SPECIALTIES_FILE, {
    'backend': '🔧 Backend разработчик',
    'frontend': '🎨 Frontend разработчик',
    'fullstack': '💼 Full-stack разработчик',
    'data_science': '📊 Data Scientist',
    'devops': '⚙️ DevOps инженер',
    'mobile': '📱 Mobile разработчик',
    'qa': '🧪 QA инженер',
})

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

Я помогу вам найти подходящие курсы, соответствующие вашему уровню и специальности.

Давайте начнём с небольшого теста, чтобы определить вашу идеальную специальность!
    """,
    'test_intro': """
🎯 Тест определения специальности

Я задам вам 7 вопросов. Выбирайте вариант, который вам больше нравится.

Начнём! 👇
    """,
    'test_result': """
✅ Вот ваша идеальная специальность: {specialty}

Теперь я покажу вам курсы, которые идеально подходят для {specialty_lower}! 📚
    """,
    'no_courses': """
😕 Извините, курсов для этой специальности пока нет.

Попробуйте позже или посмотрите все доступные курсы!
    """,
}

# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def get_courses_by_specialty(specialty: str) -> Dict[str, Dict]:
    """Получить курсы по специальности"""
    return {
        course_id: course 
        for course_id, course in COURSES_DATA.items()
        if specialty in course.get('specialty', [])
    }

def get_specialty_name(specialty: str) -> str:
    """Получить название специальности"""
    return SPECIALTIES.get(specialty, 'Неизвестная специальность')

print("✅ Config загружен успешно!")
