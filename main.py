"""
Точка входа приложения
"""
import asyncio
import logging
from app.bot import main

if __name__ == '__main__':
    asyncio.run(main())
