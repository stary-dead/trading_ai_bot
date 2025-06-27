#!/usr/bin/env python3
"""
Точка входа для торгового ИИ бота
"""

import sys
import os
import asyncio
import logging

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Основная точка входа"""
    try:
        # Проверяем конфигурацию перед запуском
        from src.trading_ai_bot.config import validate_config
        
        print("Проверка конфигурации...")
        validate_config()
        print("✓ Конфигурация корректна")
        
        if len(sys.argv) > 1 and sys.argv[1] == 'server':
            # Запуск сервера
            from src.trading_ai_bot.server import main as server_main
            asyncio.run(server_main())
        else:
            # Запуск legacy режима
            from main_legacy import main as legacy_main
            asyncio.run(legacy_main())
            
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("\nПожалуйста, проверьте файл .env и убедитесь, что все необходимые переменные установлены.")
        print("Используйте env.example как образец.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
