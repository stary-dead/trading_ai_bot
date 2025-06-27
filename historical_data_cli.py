#!/usr/bin/env python3
"""
CLI скрипт для Historical Data Tool
"""

import sys
from pathlib import Path

# Добавляем путь к модулю в sys.path для возможности импорта
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

# Импортируем и запускаем главную функцию CLI
from trading_ai_bot.tools.historical_data.__main__ import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
