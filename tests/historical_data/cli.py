#!/usr/bin/env python3
"""
CLI модуль для Historical Data Tool - исполняемая версия
Запуск: python -m tests.historical_data.cli
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Импортируем и запускаем главную функцию CLI
from trading_ai_bot.tools.historical_data.__main__ import main

if __name__ == "__main__":
    asyncio.run(main())
