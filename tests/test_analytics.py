"""
Тесты для аналитики
"""
import pytest
from analytics.analyzer import get_courses_statistics

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
