"""
Конфигурация для pytest
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def event_loop():
    """Fixture для event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_user_data():
    """Mock данные пользователя"""
    return {
        'user_id': 123456,
        'name': 'Test User',
        'specialty': 'backend',
        'courses': ['python_fundamentals', 'django_web'],
        'progress': {
            'python_fundamentals': {'completed': 5},
            'django_web': {'completed': 3}
        }
    }

@pytest.fixture
def test_data_dir(tmp_path):
    """Временная директория для тестирования"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
