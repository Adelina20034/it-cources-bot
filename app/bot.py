"""
Основной бот на aiogram 3.x
Запуск и обработка всех команд и сообщений
"""
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, StateFilter

from app.config import TELEGRAM_BOT_TOKEN
from app.handlers import (
    start_command,
    handle_test_start,
    handle_test_answer,
    handle_courses_list,
    handle_course_selection,
    handle_enroll,
    handle_schedule_list,
    handle_my_courses_list,
    handle_my_course_detail,
    handle_my_lessons,
    handle_mark_progress,
    handle_complete_progress,
    handle_progress_list,
    handle_faq_list,
    handle_faq_selection,
    handle_stats_list,
    handle_back_to_main
)
from app.states import TestState
from app.database import init_databases

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    
    await init_databases()
    
    # ✅ Правильный способ для aiogram 3.7.0+
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=default_properties)
    dp = Dispatcher()
    
    # MESSAGE HANDLERS
    dp.message.register(start_command, Command("start"))
    
    # CALLBACK HANDLERS - ТЕСТ
    dp.callback_query.register(handle_test_start, F.data == "test_start")
    dp.callback_query.register(handle_test_answer, StateFilter(TestState.waiting_for_answer))
    
    # CALLBACK HANDLERS - КУРСЫ
    dp.callback_query.register(handle_courses_list, F.data == "courses_list")
    dp.callback_query.register(handle_course_selection, F.data.startswith("course_"))
    dp.callback_query.register(handle_enroll, F.data.startswith("enroll_"))
    
    # CALLBACK HANDLERS - РАСПИСАНИЕ
    dp.callback_query.register(handle_schedule_list, F.data == "schedule_list")
    
    # CALLBACK HANDLERS - МОИ КУРСЫ
    dp.callback_query.register(handle_my_courses_list, F.data == "my_courses_list")
    dp.callback_query.register(handle_my_course_detail, F.data.startswith("my_course_"))
    dp.callback_query.register(handle_my_lessons, F.data.startswith("my_lessons_"))
    dp.callback_query.register(handle_mark_progress, F.data.startswith("mark_progress_"))
    dp.callback_query.register(handle_complete_progress, F.data.startswith("complete_progress_"))
    
    # CALLBACK HANDLERS - ПРОГРЕСС
    dp.callback_query.register(handle_progress_list, F.data == "progress_list")
    
    # CALLBACK HANDLERS - FAQ
    dp.callback_query.register(handle_faq_list, F.data == "faq_list")
    dp.callback_query.register(handle_faq_selection, F.data.startswith("faq_"))
    
    # CALLBACK HANDLERS - СТАТИСТИКА
    dp.callback_query.register(handle_stats_list, F.data == "stats_list")
    
    # CALLBACK HANDLERS - НАВИГАЦИЯ
    dp.callback_query.register(handle_back_to_main, F.data == "back_to_main")
    
    try:
        logger.info("🚀 Бот запущен! Слушаю сообщения...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
