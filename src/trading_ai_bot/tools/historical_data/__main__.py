"""
CLI модуль для Historical Data Tool
Позволяет запускать инструмент через python -m
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем путь к модулю в sys.path для возможности импорта
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trading_ai_bot.tools.historical_data import HistoricalDataTool

# Попробуем импортировать config, если не получится - используем базовую конфигурацию
try:
    from trading_ai_bot.config import get_config
except ImportError:
    def get_config():
        return {
            'exchange': {
                'base_url': 'https://fapi.binance.com'
            },
            'historical_data': {
                'cache_db_path': 'historical_data.db'
            }
        }


async def main():
    """Основная функция CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Historical Data Tool CLI')
    parser.add_argument('--symbol', required=True, help='Торговая пара (например, BTCUSDT)')
    parser.add_argument('--days', type=int, default=30, help='Количество дней для загрузки')
    parser.add_argument('--interval', default='15m', 
                       choices=['1m', '5m', '15m', '1h', '4h', '1d'], 
                       help='Интервал')
    parser.add_argument('--action', 
                       choices=['load', 'export', 'info'], 
                       default='load',
                       help='Действие: load (загрузить данные), export (экспортировать), info (информация о кэше)')
    parser.add_argument('--format', default='csv', 
                       choices=['csv', 'json'], 
                       help='Формат экспорта')
    parser.add_argument('--output', help='Путь к файлу для экспорта')
    
    args = parser.parse_args()
    
    try:
        # Загружаем конфигурацию
        config = get_config()
        
        # Создаем инструмент
        async with HistoricalDataTool(config) as tool:
            
            if args.action == 'load':
                print(f"Загрузка данных {args.symbol} за {args.days} дней ({args.interval})...")
                
                end_date = datetime.now()
                start_date = end_date - timedelta(days=args.days)
                
                result = await tool.load_data(
                    symbol=args.symbol,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    interval=args.interval
                )
                
                if result['success']:
                    print(f"✅ Загружено {result['records_count']} записей")
                    print(f"Валидация: {'✅ Успешно' if result['validation']['is_valid'] else '❌ Есть ошибки'}")
                    print(f"Кэширование: {'✅ Успешно' if result['cached'] else '❌ Ошибка'}")
                else:
                    print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
            elif args.action == 'export':
                if not args.output:
                    args.output = f"{args.symbol}_{args.interval}.{args.format}"
                
                print(f"Экспорт данных {args.symbol} в {args.output}...")
                
                result = tool.export_data(
                    symbol=args.symbol,
                    format=args.format,
                    file_path=args.output,
                    interval=args.interval
                )
                
                if result['success']:
                    print(f"✅ Данные экспортированы в {args.output}")
                else:
                    print(f"❌ Ошибка экспорта: {result.get('error', 'Неизвестная ошибка')}")
            
            elif args.action == 'info':
                print(f"Информация о кэшированных данных {args.symbol} ({args.interval})...")
                
                result = tool.get_available_data_range(
                    symbol=args.symbol,
                    interval=args.interval
                )
                
                if result['success']:
                    print(f"✅ Доступные данные:")
                    print(f"   Период: {result['min_date']} - {result['max_date']}")
                    print(f"   Записей: {result['records_count']}")
                else:
                    print(f"❌ {result.get('message', 'Нет данных в кэше')}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
