# Trading AI Bot - MCP Server

Интеллектуальный торговый агент для фьючерсных рынков с поддержкой Model Context Protocol (MCP).

## Структура проекта

```
trading_ai_bot/
├── src/
│   └── trading_ai_bot/
│       ├── __init__.py
│       ├── server.py           # MCP сервер
│       └── core/
│           ├── __init__.py
│           ├── trading_agent.py    # Основной торговый агент
│           ├── data_provider.py    # Поставщик данных Binance
│           ├── claude_analyzer.py  # ИИ анализатор с Claude
│           ├── risk_manager.py     # Управление рисками
│           └── technical_analyzer.py # Технический анализ
├── config.json             # Конфигурация
├── requirements.txt        # Зависимости
├── pyproject.toml         # Настройки проекта
└── README.md
```

## Возможности

- **ИИ анализ**: Использует Claude AI для анализа рынка
- **Технический анализ**: RSI, MACD, Bollinger Bands, Volume Profile
- **Управление рисками**: Kelly Criterion, позиционное управление
- **MCP интеграция**: Полная поддержка Model Context Protocol
- **Мультитаймфрейм**: Анализ на разных временных интервалах

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -e .
```

3. Настройте конфигурацию в `config.json`

## Использование

### Запуск MCP сервера
```bash
trading-ai-server
```

### Доступные инструменты MCP

- `get_market_data` - получение данных рынка
- `analyze_market` - ИИ анализ рынка  
- `get_technical_analysis` - технические индикаторы
- `calculate_position_size` - расчет размера позиции
- `get_portfolio_summary` - сводка портфеля
- `execute_trade_decision` - выполнение торгового решения
- `configure_system` - настройка системы

## Конфигурация

Пример `config.json`:

```json
{
  "trading": {
    "initial_balance": 10000,
    "max_risk_per_trade": 0.02,
    "trading_pairs": ["BTCUSDT", "ETHUSDT"]
  },
  "exchange": {
    "base_url": "https://fapi.binance.com"
  },
  "ai": {
    "claude_api_key": "your_claude_api_key",
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 3000
  }
}
```

## Лицензия

MIT
