"""
Тесты для аналитики
"""
import pytest
import numpy as np
from analytics.analyzer import CoursesAnalyzer

@pytest.mark.asyncio
async def test_get_statistics():
    """Тест получения статистики"""
    analyzer = CoursesAnalyzer()
    stats = await analyzer.get_statistics()
    
    assert 'total_users' in stats
    assert 'total_enrollments' in stats
    assert 'avg_progress' in stats
    assert 'popular_courses' in stats
    
    assert stats['total_users'] >= 0
    assert stats['total_enrollments'] >= 0
    assert 0 <= stats['avg_progress'] <= 100

@pytest.mark.asyncio
async def test_get_course_dataframe():
    """Тест получения DataFrame курсов"""
    analyzer = CoursesAnalyzer()
    df = await analyzer.get_course_dataframe()
    
    assert len(df) > 0
    assert 'name' in df.columns
    assert 'price' in df.columns
    assert 'lessons' in df.columns

@pytest.mark.asyncio
async def test_get_user_dataframe():
    """Тест получения DataFrame пользователей"""
    analyzer = CoursesAnalyzer()
    df = await analyzer.get_user_dataframe()
    
    assert 'user_id' in df.columns
    assert 'specialty' in df.columns
    assert 'courses_count' in df.columns
