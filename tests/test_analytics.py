"""
Тесты для аналитики
"""
import pytest
from analytics.analyzer import generate_statistics_chart, get_courses_statistics

@pytest.mark.asyncio
async def test_get_statistics():
    """Тест получения статистики"""
    stats = await get_courses_statistics()
    
    assert 'total_users' in stats
    assert 'total_enrollments' in stats
    assert 'avg_progress' in stats
    assert 'popular_courses' in stats
    
    assert stats['total_users'] >= 0
    assert stats['total_enrollments'] >= 0
    assert 0 <= stats['avg_progress'] <= 100
    assert isinstance(stats['popular_courses'], dict)


@pytest.mark.asyncio
async def test_generate_statistics_chart():
    """График генерируется корректно"""
    stats = {
        'total_users': 3,
        'avg_progress': 50.0,
        'popular_courses': {
            'Python': 2,
            'Django': 1
        },
        '_progress_list': [20, 50, 80]
    }
    
    chart_buffer = await generate_statistics_chart(stats)
    
    # Проверяем, что вернулся буфер
    assert chart_buffer is not None
    
    # Проверяем, что не пустой
    chart_buffer.seek(0)
    data = chart_buffer.read()
    assert len(data) > 0
    
    # Проверяем, что это PNG
    assert data[:8] == b'\x89PNG\r\n\x1a\n'  # Сигнатура PNG

@pytest.mark.asyncio
async def test_generate_chart_empty_data():
    """График с пустыми данными не падает"""
    stats = {
        'total_users': 0,
        'avg_progress': 0.0,
        'popular_courses': {},
        '_progress_list': []
    }
    
    chart_buffer = await generate_statistics_chart(stats)
    
    # Должен вернуть None или пустой буфер
    # (в зависимости от реализации)
    assert chart_buffer is None or len(chart_buffer.getvalue()) == 0