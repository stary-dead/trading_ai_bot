#!/usr/bin/env python3
"""
Legacy точка входа для совместимости
Запускает торгового агента в классическом режиме
"""

import asyncio
import json
import logging
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trading_ai_bot.core.trading_agent import TradingAgent

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

async def main():
    """Главная функция для запуска в legacy режиме"""
    print("Запуск торгового агента в legacy режиме...")
    
    # Загружаем конфигурацию из файла
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("[ERROR] Файл config.json не найден. Используется конфигурация по умолчанию.")
        config = {
            "trading": {
                "initial_balance": 10000,
                "max_risk_per_trade": 0.02,
                "trading_pairs": ["BTCUSDT", "ETHUSDT"]
            },
            "exchange": {},
            "ai": {"debug_mode": False}
        }
    
    # Проверяем дебаг режим
    debug_mode = config.get('ai', {}).get('debug_mode', False)
    
    if debug_mode:
        print("[DEBUG] ДЕБАГ РЕЖИМ АКТИВЕН - ИИ не используется, только fallback функции")
        config['ai']['debug_mode'] = True
    else:
        print("[AI] Обычный режим - используется ИИ анализ")
    
    # Объединяем конфигурацию для торгового агента
    agent_config = {
        **config.get('trading', {}),
        'exchange': config.get('exchange', {}),
        'ai': config.get('ai', {})
    }
    
    # Создаем и запускаем агента
    agent = TradingAgent(agent_config)
    
    print("[SUCCESS] Торговый агент инициализирован")
    print("[INFO] Запуск основного цикла торговли...")
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\n[STOP] Получен сигнал остановки")
    except Exception as e:
        print(f"[ERROR] Ошибка в работе агента: {e}")
    finally:
        print("[FINISH] Торговый агент остановлен")

if __name__ == "__main__":
    asyncio.run(main())
