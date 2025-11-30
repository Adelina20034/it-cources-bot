"""
Анализ данных и статистика курсов
Использует numpy, pandas, matplotlib, seaborn
"""
import io
from typing import Dict, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
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
        
        # NUMPY: Вычисление среднего
        avg_progress = float(np.mean(progress_list)) if progress_list else 0.0
        
        popular_courses = {}
        sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
        
        for course_id, count in sorted_courses[:5]:
            if course_id in COURSES_DATA:
                popular_courses[COURSES_DATA[course_id]['name']] = count
        
        return {
            'total_users': total_users,
            'total_enrollments': total_enrollments,
            'avg_progress': float(avg_progress),
            'popular_courses': popular_courses,
            # Дополнительно для графиков
            '_progress_list': progress_list,
            '_course_counts': course_counts
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


async def generate_statistics_chart(stats: Dict) -> Optional[io.BytesIO]:
    """
    Генерирует простые графики статистики
    
    Args:
        stats: Результат get_courses_statistics()
    
    Returns:
        BytesIO с изображением для отправки в Telegram
    """
    try:
        progress_list = stats.get('_progress_list', [])
        popular_courses = stats.get('popular_courses', {})
        
        if not progress_list and not popular_courses:
            return None
        
        # Создаём фигуру с 2 подграфиками
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # ============ ГРАФИК 1: СТОЛБЧАТАЯ ДИАГРАММА (MATPLOTLIB) ============
        # Популярные курсы по количеству студентов
        
        if popular_courses:
            # ✨ PANDAS: Создаём DataFrame
            df = pd.DataFrame([
                {'course': name, 'count': count}
                for name, count in popular_courses.items()
            ])
            
            # ✨ MATPLOTLIB: Простая столбчатая диаграмма
            # courses = df['course'].tolist()
            courses = [course[1:] if len(course) > 0 else course for course in df['course'].tolist()]
            counts = df['count'].tolist()
            
            # Создаём столбцы
            bars = ax1.bar(
                range(len(courses)),  # Позиции столбцов: 0, 1, 2, 3, 4
                counts,               # Высота столбцов
                color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'],  # Цвета
                edgecolor='black',    # Чёрная обводка
                linewidth=1.5
            )
            
            # Настройка осей
            ax1.set_xlabel('Курсы', fontsize=12, weight='bold')
            ax1.set_ylabel('Количество студентов', fontsize=12, weight='bold')
            ax1.set_title('Популярные курсы', fontsize=14, weight='bold', pad=15)
            ax1.set_xticks(range(len(courses)))
            ax1.set_xticklabels(courses, rotation=45, ha='right', fontsize=10)
            
            # ✨ НОВОЕ: Устанавливаем только целые числа на оси Y
            max_count = max(counts)
            # Если максимум <= 10, шаг = 1, иначе автоматически
            if max_count <= 10:
                ax1.set_yticks(range(0, max_count + 2))  # 0, 1, 2, 3, ...
            else:
                # Для больших чисел используем целые шаги
                from matplotlib.ticker import MaxNLocator
                ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
            
            # Устанавливаем диапазон оси Y (начинается с 0)
            ax1.set_ylim([0, max_count + 1])
            
            # Добавляем значения на столбцы
            for i, (bar, count) in enumerate(zip(bars, counts)):
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,  # X координата (центр столбца)
                    height + 0.1,                        # Y координата (чуть выше столбца)
                    f'{int(count)}',                     # Текст (количество)
                    ha='center',                         # Выравнивание по горизонтали
                    va='bottom',                         # Выравнивание по вертикали
                    fontsize=11,
                    weight='bold'
                )
            
            ax1.grid(True, alpha=0.3, axis='y')  # Сетка только по Y
        else:
            ax1.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=14)
            ax1.set_title('📊 Популярные курсы', fontsize=14, weight='bold', pad=15)
        
        # ============ ГРАФИК 2: ЛИНЕЙНЫЙ ГРАФИК (SEABORN) ============
        # Прогресс студентов (распределение)
        
        if progress_list:
            # ✨ NUMPY: Преобразуем в array и сортируем
            progress_array = np.array(progress_list)
            progress_sorted = np.sort(progress_array)  # Сортировка для линии
            
            # ✨ SEABORN: Линейный график
            sns.lineplot(
                x=range(len(progress_sorted)),  # X: номер студента (0, 1, 2, ...)
                y=progress_sorted,              # Y: процент прогресса
                ax=ax2,
                color='#e74c3c',                # Красный цвет
                linewidth=2.5,
                marker='o',                     # Точки на линии
                markersize=6
            )
            
            # Настройка графика
            ax2.set_xlabel('Студент (по возрастанию прогресса)', fontsize=12, weight='bold')
            ax2.set_ylabel('Прогресс (%)', fontsize=12, weight='bold')
            ax2.set_title('Распределение прогресса студентов', fontsize=14, weight='bold', pad=15)
            
            # Горизонтальная линия среднего значения
            avg = stats['avg_progress']
            ax2.axhline(
                y=avg,
                color='green',
                linestyle='--',
                linewidth=2,
                label=f'Среднее: {avg:.1f}%'
            )
            
            ax2.legend(fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim([0, 105])  # Ось Y от 0 до 105%
            from matplotlib.ticker import MaxNLocator
            ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            ax2.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=14)
            ax2.set_title('📈 Распределение прогресса студентов', fontsize=14, weight='bold', pad=15)
        
        plt.tight_layout()
        
        # Сохранение в память
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    except Exception as e:
        print(f"❌ Ошибка при создании графика: {e}")
        import traceback
        traceback.print_exc()
        return None
