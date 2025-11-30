"""
Unittest тесты для основных функций
"""
import unittest
from app.config import SPECIALTIES, COURSES_DATA, FAQ_DATA

class TestConfig(unittest.TestCase):
    """Тесты конфигурации"""
    
    def test_specialties_exist(self):
        """Проверка наличия специальностей"""
        self.assertGreater(len(SPECIALTIES), 0)
        self.assertIn('backend', SPECIALTIES)
        self.assertIn('frontend', SPECIALTIES)
        self.assertIn('fullstack', SPECIALTIES)
        self.assertIn('data_science', SPECIALTIES)
        self.assertIn('devops', SPECIALTIES)
        self.assertIn('mobile', SPECIALTIES)
        self.assertIn('qa', SPECIALTIES)

    def test_courses_exist(self):
        """Проверка наличия курсов"""
        self.assertGreater(len(COURSES_DATA), 0)
        
        for course_id, course in COURSES_DATA.items():
            self.assertIn('name', course)
            self.assertIn('description', course)
            self.assertIn('price', course)
            self.assertIn('lessons', course)
            self.assertGreater(course['price'], 0)
            self.assertGreater(course['lessons'], 0)
    
    def test_faq_data(self):
        """Проверка FAQ данных"""
        self.assertGreater(len(FAQ_DATA), 0)
        
        for faq_id, faq_item in FAQ_DATA.items():
            self.assertIn('question', faq_item)
            self.assertIn('answer', faq_item)
            self.assertGreater(len(faq_item['question']), 0)
            self.assertGreater(len(faq_item['answer']), 0)

class TestCourseData(unittest.TestCase):
    """Тесты данных курсов"""
    
    def test_course_specialties_valid(self):
        """Проверка что специальности курсов валидны"""
        for course_id, course in COURSES_DATA.items():
            for specialty in course.get('specialty', []):
                self.assertIn(specialty, SPECIALTIES,
                            f"Специальность {specialty} в курсе {course_id} не существует")
    
    def test_course_schedule_not_empty(self):
        """Проверка расписания"""
        for course_id, course in COURSES_DATA.items():
            self.assertGreater(len(course.get('schedule', [])), 0,
                             f"Расписание для курса {course_id} пусто")
    
    def test_course_lessons_list(self):
        """Проверка списка уроков"""
        for course_id, course in COURSES_DATA.items():
            lessons = course.get('lessons_list', [])
            lessons_count = course.get('lessons', 0)
            
            self.assertEqual(len(lessons), lessons_count,
                           f"Количество уроков не совпадает для {course_id}")

if __name__ == '__main__':
    unittest.main()
