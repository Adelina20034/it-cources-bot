"""
Работа с локальной БД (JSON)
"""
import json
import os
import asyncio
from typing import Dict, List, Optional
from app.config import USERS_FILE

class Database:
    """Класс для работы с JSON БД"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = asyncio.Lock()
    
    async def load(self) -> Dict:
        """Загрузить данные из файла"""
        async with self.lock:
            if os.path.exists(self.file_path):
                try:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    return {}
            return {}
    
    async def save(self, data: Dict) -> None:
        """Сохранить данные в файл"""
        async with self.lock:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

# Инициализация БД
users_db = Database(USERS_FILE)

async def get_user(user_id: int) -> Optional[Dict]:
    """Получить пользователя"""
    data = await users_db.load()
    return data.get(str(user_id))

async def save_user(user_id: int, user_data: Dict) -> None:
    """Сохранить пользователя"""
    data = await users_db.load()
    data[str(user_id)] = user_data
    await users_db.save(data)

async def get_user_courses(user_id: int) -> List[str]:
    """Получить курсы пользователя"""
    user = await get_user(user_id)
    return user.get('courses', []) if user else []

async def add_user_course(user_id: int, course_id: str) -> None:
    """Добавить курс пользователю"""
    user = await get_user(user_id)
    if user:
        if course_id not in user.get('courses', []):
            user['courses'].append(course_id)
            if 'progress' not in user:
                user['progress'] = {}
            user['progress'][course_id] = {'completed': 0}
            await save_user(user_id, user)

async def get_user_progress(user_id: int, course_id: str):
    """Получить прогресс пользователя по курсу"""
    user = await get_user(user_id)
    if user and 'progress' in user:
        return user['progress'].get(course_id, {'completed': 0})
    return {'completed': 0}

async def get_all_users() -> Dict:
    """Получить всех пользователей"""
    return await users_db.load()
