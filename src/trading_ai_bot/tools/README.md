# Trading AI Bot Tools

Модульная структура инструментов для MCP сервера торгового ИИ бота.

## Структура

```
tools/
├── __init__.py              # Общие экспорты и объединение MCP tools
├── market_data/            # Инструменты для получения рыночных данных
│   ├── __init__.py
│   └── tool.py             # MarketDataTool + MCP схемы
├── technical_analysis/     # Инструменты технического анализа
│   ├── __init__.py
│   └── tool.py             # TechnicalAnalysisTool + MCP схемы
├── analysis_formatter/     # Форматирование данных для ИИ
│   ├── __init__.py
│   └── tool.py             # AnalysisFormatterTool
├── analysis_validator/     # Валидация торговых параметров
│   ├── __init__.py
│   └── tool.py             # AnalysisValidatorTool
├── mock_analyzer/          # Mock и fallback анализ
│   ├── __init__.py
│   └── tool.py             # MockAnalyzerTool
├── prompt_builder/         # Создание промптов для ИИ
│   ├── __init__.py
│   └── tool.py             # PromptBuilderTool
└── README.md               # Этот файл
```

## Market Data Tools

### MarketDataTool
Инструмент для получения рыночных данных с Binance Futures API.

**MCP Methods:**
- `market_data.get_current_price` - Получить текущую цену
- `market_data.get_klines` - Получить свечные данные
- `market_data.get_24hr_ticker` - Получить 24-часовую статистику
- `market_data.get_multi_timeframe_data` - Данные с нескольких таймфреймов
- `market_data.get_market_data` - Полные рыночные данные

**Пример использования:**
```python
from trading_ai_bot.tools.market_data import MarketDataTool

async with MarketDataTool(config) as tool:
    price = await tool.get_current_price("BTCUSDT")
    klines = await tool.get_klines("BTCUSDT", "15m", 100)
```

## Technical Analysis Tools

### TechnicalAnalysisTool
Инструмент для технического анализа с расчетом индикаторов.

**MCP Methods:**
- `technical_analysis.calculate_rsi` - Рассчитать RSI
- `technical_analysis.calculate_macd` - Рассчитать MACD
- `technical_analysis.calculate_bollinger_bands` - Полосы Боллинджера
- `technical_analysis.calculate_volume_profile` - Профиль объема и VWAP
- `technical_analysis.calculate_support_resistance` - Уровни поддержки/сопротивления
- `technical_analysis.analyze_multiple_timeframes` - Мультитаймфрейм анализ
- `technical_analysis.comprehensive_analysis` - Полный технический анализ

**Пример использования:**
```python
from trading_ai_bot.tools.technical_analysis import TechnicalAnalysisTool

tool = TechnicalAnalysisTool()
rsi = tool.calculate_rsi(prices, period=14)
analysis = tool.comprehensive_analysis(market_data)
```

## Analysis Formatter Tools

### AnalysisFormatterTool
Инструмент для форматирования рыночных и технических данных в удобочитаемый формат для анализа ИИ.

**Основные методы:**
- `format_comprehensive_market_data()` - Полное форматирование рыночных данных
- `format_technical_indicators()` - Форматирование технических индикаторов
- `format_volume_analysis()` - Форматирование анализа объемов
- `format_support_resistance()` - Форматирование уровней поддержки/сопротивления
- `format_multi_timeframe_analysis()` - Форматирование мульти-таймфрейм анализа
- `format_recent_candles()` - Форматирование последних свечей

## Analysis Validator Tools

### AnalysisValidatorTool
Инструмент для валидации и коррекции результатов торгового анализа от ИИ.

**Основные методы:**
- `validate_enhanced_analysis()` - Валидация и коррекция анализа
- `get_enhanced_default_value()` - Получение значений по умолчанию

**Проверки:**
- Корректность цен входа (не более 5% от текущей цены)
- Стоп-лосс не более 3% риска
- Минимальное соотношение риск/прибыль 1:2
- Размер позиции не более 10% капитала

## Mock Analyzer Tools

### MockAnalyzerTool
Инструмент для создания mock и fallback анализа когда ИИ недоступен.

**Основные методы:**
- `create_enhanced_mock_analysis()` - Умный mock анализ на основе технических индикаторов
- `create_fallback_analysis()` - Консервативный fallback анализ при ошибках

**Логика mock анализа:**
- Анализ RSI, MACD, Bollinger Bands
- Учет объемов и трендов
- Подсчет бычьих/медвежьих сигналов
- Определение sentiment и confidence

## Prompt Builder Tools

### PromptBuilderTool
Инструмент для создания промптов для анализа ИИ.

**Основные методы:**
- `create_enhanced_analysis_prompt()` - Создание детального промпта для торгового анализа

**Особенности промпта:**
- Ролевая модель опытного трейдера
- Четкая структура анализа
- Строгие требования к риск-менеджменту
- JSON формат ответа

## MCP Integration

Все инструменты автоматически экспортируются как MCP tools с соответствующими схемами:

```python
from trading_ai_bot.tools import ALL_MCP_TOOLS

# Получить все доступные MCP инструменты
tools_schema = ALL_MCP_TOOLS

# Использовать в MCP сервере
from trading_ai_bot.mcp_config import create_mcp_server_config

mcp_config = create_mcp_server_config()
result = await mcp_config.call_tool("market_data.get_current_price", {"symbol": "BTCUSDT"})
```

## Преимущества модульной структуры

1. **Разделение ответственности** - каждый инструмент в своей папке
2. **MCP совместимость** - автоматические схемы для каждого tool
3. **Переиспользование** - инструменты можно использовать независимо
4. **Тестируемость** - легко тестировать каждый инструмент отдельно
5. **Расширяемость** - легко добавлять новые инструменты

## Добавление нового инструмента

1. Создать папку в `tools/`
2. Создать `__init__.py` и `tool.py`
3. Определить класс инструмента и `MCP_TOOLS` схему
4. Добавить импорт в основной `tools/__init__.py`
5. Обновить `mcp_config.py` для маршрутизации

Пример структуры нового инструмента:
```python
# tools/new_tool/tool.py
class NewTool:
    def method_name(self, arg1: str) -> Dict:
        pass

MCP_TOOLS = {
    "method_name": {
        "description": "Описание метода",
        "parameters": { ... }
    }
}
```
