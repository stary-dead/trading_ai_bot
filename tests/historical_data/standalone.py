#!/usr/bin/env python3
"""
Standalone тест для Historical Data Tool
Запуск: python -m tests.historical_data.standalone
"""

import asyncio
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from trading_ai_bot.tools.historical_data import HistoricalDataTool


def setup_logging(level: str = "INFO"):
    """Настройка логирования"""
    # Создаем директорию для логов относительно корня проекта
    logs_dir = project_root / "logs" / "historical_data"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Настраиваем логирование с правильной кодировкой
    log_file = logs_dir / "standalone_test.log"
    
    # Создаем форматтер без эмоджи
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Очищаем существующие handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler с UTF-8 кодировкой
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_test_config():
    """Получение тестовой конфигурации"""
    return {
        'exchange': {
            'base_url': 'https://fapi.binance.com'
        },
        'historical_data': {
            'cache_db_path': str(project_root / 'tests' / 'data' / 'test_historical_data.db')
        }
    }


async def test_load_data(tool: HistoricalDataTool, symbol: str, days: int, interval: str):
    """Тест загрузки данных"""
    print(f"\n=== Тест загрузки данных ===")
    print(f"Символ: {symbol}")
    print(f"Дней: {days}")
    print(f"Интервал: {interval}")
    
    # Рассчитываем даты
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Загружаем данные
    result = await tool.load_data(
        symbol=symbol,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval=interval
    )
    
    print(f"Результат: {json.dumps(result, indent=2, default=str)}")
    return result


async def test_cached_data(tool: HistoricalDataTool, symbol: str, days: int, interval: str):
    """Тест получения кэшированных данных"""
    print(f"\n=== Тест кэшированных данных ===")
    
    # Рассчитываем даты
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Получаем кэшированные данные
    result = tool.get_cached_data(
        symbol=symbol,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval=interval
    )
    
    print(f"Количество записей в кэше: {result.get('records_count', 0)}")
    print(f"Успех: {result.get('success', False)}")
    return result


async def test_data_range(tool: HistoricalDataTool, symbol: str, interval: str):
    """Тест получения диапазона данных"""
    print(f"\n=== Тест диапазона данных ===")
    
    result = tool.get_available_data_range(symbol=symbol, interval=interval)
    print(f"Результат: {json.dumps(result, indent=2, default=str)}")
    return result


async def test_export_data(tool: HistoricalDataTool, symbol: str, interval: str, export_format: str):
    """Тест экспорта данных"""
    print(f"\n=== Тест экспорта данных ===")
    
    # Создаем директорию для экспорта в папке tests
    export_dir = project_root / "tests" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = export_dir / f"{symbol}_{interval}.{export_format}"
    
    result = tool.export_data(
        symbol=symbol,
        format=export_format,
        file_path=str(file_path),
        interval=interval
    )
    
    print(f"Экспорт в {file_path}: {result.get('success', False)}")
    
    # Проверяем существование файла
    if file_path.exists():
        file_size = file_path.stat().st_size
        print(f"Размер файла: {file_size} байт")
    
    return result


async def test_validation(tool: HistoricalDataTool):
    """Тест валидации данных"""
    print(f"\n=== Тест валидации данных ===")
    
    # Создаем тестовые данные с ошибками
    test_data = [
        {
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'open': 45000.0,
            'high': 45500.0,
            'low': 44500.0,
            'close': 45200.0,
            'volume': 1000.0
        },
        {
            'timestamp': datetime(2024, 1, 1, 12, 15, 0),
            'open': 45200.0,
            'high': 44000.0,  # Ошибка: high меньше open
            'low': 44500.0,   # Ошибка: low больше high
            'close': 45300.0,
            'volume': -100.0  # Ошибка: отрицательный объем
        },
        {
            'timestamp': datetime(2024, 1, 1, 12, 15, 0),  # Дубликат timestamp
            'open': 45300.0,
            'high': 45800.0,
            'low': 45100.0,
            'close': 45600.0,
            'volume': 800.0
        }
    ]
    
    result = tool.validate_data(test_data, "TESTUSDT", "15m")
    print(f"Результат валидации: {json.dumps(result, indent=2, default=str)}")
    return result


async def main():
    """Основная функция для тестирования"""
    parser = argparse.ArgumentParser(description='Тест Historical Data Tool')
    parser.add_argument('--symbol', default='BTCUSDT', help='Торговая пара')
    parser.add_argument('--days', type=int, default=7, help='Количество дней для загрузки')
    parser.add_argument('--interval', default='15m', choices=['1m', '5m', '15m', '1h', '4h', '1d'], help='Интервал')
    parser.add_argument('--export-format', default='csv', choices=['csv', 'json'], help='Формат экспорта')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Уровень логирования')
    parser.add_argument('--test', nargs='*', 
                       choices=['load', 'cache', 'range', 'export', 'validation', 'all'],
                       default=['all'], help='Какие тесты запустить')
    
    args = parser.parse_args()
    
    # Настраиваем логирование
    setup_logging(args.log_level)
    
    print("=== Тестирование Historical Data Tool ===")
    print(f"Символ: {args.symbol}")
    print(f"Дней: {args.days}")
    print(f"Интервал: {args.interval}")
    print(f"Формат экспорта: {args.export_format}")
    print(f"Тесты: {args.test}")
    print(f"Логи сохраняются в: {project_root / 'logs' / 'historical_data'}")
    
    # Создаем инструмент
    config = get_test_config()
    
    async with HistoricalDataTool(config) as tool:
        
        # Определяем какие тесты запускать
        tests_to_run = args.test
        if 'all' in tests_to_run:
            tests_to_run = ['load', 'cache', 'range', 'export', 'validation']
        
        results = {}
        
        # Запускаем тесты
        if 'load' in tests_to_run:
            results['load'] = await test_load_data(tool, args.symbol, args.days, args.interval)
        
        if 'cache' in tests_to_run:
            results['cache'] = await test_cached_data(tool, args.symbol, args.days, args.interval)
        
        if 'range' in tests_to_run:
            results['range'] = await test_data_range(tool, args.symbol, args.interval)
        
        if 'export' in tests_to_run:
            results['export'] = await test_export_data(tool, args.symbol, args.interval, args.export_format)
        
        if 'validation' in tests_to_run:
            results['validation'] = await test_validation(tool)
        
        # Выводим сводку результатов
        print(f"\n=== Сводка результатов ===")
        for test_name, result in results.items():
            success = result.get('success', False) if isinstance(result, dict) else False
            status = "[УСПЕХ]" if success else "[ОШИБКА]"
            print(f"{test_name.upper()}: {status}")
        
        print(f"\nТестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
