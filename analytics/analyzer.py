"""
Анализ данных и статистика курсов
"""
from typing import Dict
from app.database import get_all_users
from app.config import COURSES_DATA

async def get_courses_statistics() -> Dict:
    """Получить статистику курсов"""
    try:
        users_data = await get_all_users()
        
        total_users = len(users_data)
        total_enrollments = 0
        
        course_counts = {}
        progress_list = []
        
        for user in users_data.values():
            courses = user.get('courses', [])
            total_enrollments += len(courses)
            
            for course_id in courses:
                course_counts[course_id] = course_counts.get(course_id, 0) + 1
            
            for course_id, progress in user.get('progress', {}).items():
                if course_id in COURSES_DATA:
                    completed = progress.get('completed', 0)
                    total = COURSES_DATA[course_id]['lessons']
                    if total > 0:
                        progress_list.append((completed / total) * 100)
        
        avg_progress = sum(progress_list) / len(progress_list) if progress_list else 0
        
        popular_courses = {}
        sorted_courses = sorted(course_counts.items(), key=lambda x: x, reverse=True)
        
        for course_id, count in sorted_courses[:5]:
            if course_id in COURSES_DATA:
                popular_courses[COURSES_DATA[course_id]['name']] = count
        
        return {
            'total_users': total_users,
            'total_enrollments': total_enrollments,
            'avg_progress': float(avg_progress),
            'popular_courses': popular_courses
        }
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'total_users': 0,
            'total_enrollments': 0,
            'avg_progress': 0.0,
            'popular_courses': {}
        }
