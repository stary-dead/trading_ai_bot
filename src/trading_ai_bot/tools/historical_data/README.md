# Historical Data Tool

Инструмент для загрузки, кэширования и работы с историческими данными криптовалютных пар с Binance.

## Возможности

- ✅ Загрузка исторических данных с Binance (до 500 свечей за раз)
- ✅ Автоматическое склеивание больших диапазонов данных
- ✅ Локальное кэширование в SQLite базе данных
- ✅ Валидация целостности данных (проверка пропусков, дубликатов, некорректных цен)
- ✅ Поддержка разных таймфреймов (1m, 5m, 15m, 1h, 4h, 1d)
- ✅ Экспорт данных в CSV и JSON форматы
- ✅ CLI интерфейс для standalone использования

## Структура модуля

```
tools/historical_data/
├── __init__.py             # Экспорты модуля
├── tool.py                 # HistoricalDataTool - основной MCP инструмент  
├── data_loader.py          # DataLoader - загрузка данных с Binance
├── data_storage.py         # DataStorage - кэширование в SQLite
├── data_validator.py       # DataValidator - валидация данных
└── __main__.py             # CLI интерфейс
```

## Использование

### 1. Как модуль Python

```python
from trading_ai_bot.tools.historical_data import HistoricalDataTool
from trading_ai_bot.config import get_config

async def main():
    config = get_config()
    
    async with HistoricalDataTool(config) as tool:
        # Загрузка данных
        result = await tool.load_data(
            symbol="BTCUSDT",
            start_date="2024-01-01", 
            end_date="2024-01-31",
            interval="15m"
        )
        
        if result['success']:
            print(f"Загружено {result['records_count']} записей")
        
        # Экспорт данных
        export_result = tool.export_data(
            symbol="BTCUSDT",
            format="csv",
            file_path="btc_data.csv",
            interval="15m"
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 2. Через CLI

```bash
# Загрузка данных BTCUSDT за 30 дней
python -m trading_ai_bot.tools.historical_data --symbol BTCUSDT --days 30 --interval 15m --action load

# Экспорт данных в CSV
python -m trading_ai_bot.tools.historical_data --symbol BTCUSDT --interval 15m --action export --format csv --output btc_data.csv

# Информация о кэшированных данных
python -m trading_ai_bot.tools.historical_data --symbol BTCUSDT --interval 15m --action info
```

### 3. Standalone тестирование

```bash
# Запуск всех тестов
python test_historical_data.py --symbol BTCUSDT --days 7 --interval 15m

# Запуск конкретных тестов
python test_historical_data.py --symbol ETHUSDT --days 3 --test load validation

# С настройкой логирования
python test_historical_data.py --symbol BTCUSDT --days 1 --log-level DEBUG
```

## MCP Tool Methods

### `historical_data.load_data(symbol, start_date, end_date, interval)`
Загружает исторические данные за указанный период.

**Параметры:**
- `symbol`: Торговая пара (например, "BTCUSDT")
- `start_date`: Начальная дата в ISO формате ("2024-01-01")
- `end_date`: Конечная дата в ISO формате ("2024-01-31") 
- `interval`: Интервал ("1m", "5m", "15m", "1h", "4h", "1d")

**Возвращает:**
```json
{
  "success": true,
  "symbol": "BTCUSDT",
  "interval": "15m",
  "records_count": 2976,
  "validation": {...},
  "cached": true,
  "first_record": {...},
  "last_record": {...}
}
```

### `historical_data.get_cached_data(symbol, start_date, end_date, interval)`
Получает кэшированные данные за указанный период.

### `historical_data.validate_data(data)`
Валидирует данные на предмет ошибок и аномалий.

### `historical_data.export_data(symbol, format, file_path, interval)`
Экспортирует данные в файл (CSV или JSON).

### `historical_data.get_available_data_range(symbol, interval)`
Возвращает доступный диапазон данных в кэше.

## Конфигурация

В `config.json` добавлена секция `historical_data`:

```json
{
  "historical_data": {
    "cache_db_path": "data/historical_data.db",
    "supported_intervals": ["1m", "5m", "15m", "1h", "4h", "1d"],
    "max_records_per_request": 500,
    "export_directory": "data/exports"
  }
}
```

## Валидация данных

Инструмент автоматически проверяет:
- ✅ Дубликаты записей по timestamp
- ✅ Пропуски во времени между свечами
- ✅ Корректность OHLC данных (High >= max(O,C), Low <= min(O,C))
- ✅ Положительные значения цен и объемов
- ✅ Аномальные движения цены (>50% за период)
- ✅ Аномально высокие объемы (>100x медианы)

## Файлы данных

- `historical_data.db` - SQLite база данных с кэшированными данными
- `historical_data_test.log` - Лог файл для standalone тестирования
- `test_exports/` - Директория с экспортированными файлами при тестировании

## Зависимости

- `aiohttp` - HTTP клиент для запросов к Binance API
- `pandas` - Обработка данных
- `sqlite3` - Локальное кэширование (встроен в Python)
- `numpy` - Численные вычисления
