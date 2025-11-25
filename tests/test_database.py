"""
Тесты для работы с БД
"""
import pytest
import asyncio
import json
from pathlib import Path
from app.database import Database, get_user, save_user, add_user_course, update_user_progress

@pytest.mark.asyncio
async def test_database_save_and_load(test_data_dir):
    """Тест сохранения и загрузки из БД"""
    db_file = test_data_dir / "test.json"
    db = Database(str(db_file))
    
    test_data = {'key': 'value', 'number': 42}
    
    # Сохраняем
    await db.save(test_data)
    assert db_file.exists()
    
    # Загружаем
    loaded = await db.load()
    assert loaded == test_data

@pytest.mark.asyncio
async def test_get_and_save_user(test_data_dir, monkeypatch):
    """Тест получения и сохранения пользователя"""
    # Переопределяем путь к файлу
    db_file = test_data_dir / "users.json"
    monkeypatch.setattr('app.database.USERS_FILE', str(db_file))
    
    user_data = {
        'user_id': 123,
        'name': 'Test User',
        'specialty': 'backend',
        'courses': [],
        'progress': {}
    }
    
    # Сохраняем пользователя
    await save_user(123, user_data)
    
    # Получаем пользователя
    user = await get_user(123)
    assert user is not None
    assert user['name'] == 'Test User'

@pytest.mark.asyncio
async def test_add_user_course(test_data_dir, monkeypatch):
    """Тест добавления курса пользователю"""
    db_file = test_data_dir / "users.json"
    monkeypatch.setattr('app.database.USERS_FILE', str(db_file))
    
    user_data = {
        'user_id': 123,
        'name': 'Test User',
        'specialty': 'backend',
        'courses': [],
        'progress': {}
    }
    
    await save_user(123, user_data)
    await add_user_course(123, 'python_fundamentals')
    
    user = await get_user(123)
    assert 'python_fundamentals' in user['courses']
    assert 'python_fundamentals' in user['progress']

@pytest.mark.asyncio
async def test_update_user_progress(test_data_dir, monkeypatch):
    """Тест обновления прогресса пользователя"""
    db_file = test_data_dir / "users.json"
    monkeypatch.setattr('app.database.USERS_FILE', str(db_file))
    
    user_data = {
        'user_id': 123,
        'name': 'Test User',
        'specialty': 'backend',
        'courses': ['python_fundamentals'],
        'progress': {'python_fundamentals': {'completed': 0}}
    }
    
    await save_user(123, user_data)
    await update_user_progress(123, 'python_fundamentals', 5)
    
    user = await get_user(123)
    assert user['progress']['python_fundamentals']['completed'] == 5
