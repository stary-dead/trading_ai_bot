# TODO: Разработка системы исторических данных и бэктестинга

## 1. Historical Data Tool (`tools/historical_data/`)

### Структура модуля:
```
tools/historical_data/
├── __init__.py
├── tool.py                 # HistoricalDataTool - основной MCP инструмент
├── data_loader.py          # Загрузка данных из разных источников
├── data_storage.py         # Кэширование и хранение данных
└── data_validator.py       # Валидация исторических данных
```

### Функциональность:
- [x] Загрузка исторических данных с Binance (до 500 свечей за раз)
- [x] Кэширование данных локально (SQLite/CSV)
- [x] Загрузка больших диапазонов данных по частям с автоматическим склеиванием
- [x] Валидация целостности данных (проверка пропусков, дубликатов)
- [x] Поддержка разных таймфреймов (1m, 5m, 15m, 1h, 4h, 1d)
- [x] Экспорт данных в разные форматы (CSV, JSON, Parquet)
- [ ] Автоматическое обновление кэшированных данных

### MCP Tool Methods:
- [x] `historical_data.load_data(symbol, start_date, end_date, interval)`
- [x] `historical_data.cache_data(symbol, data, interval)`
- [x] `historical_data.get_cached_data(symbol, start_date, end_date, interval)`
- [x] `historical_data.validate_data(data)`
- [x] `historical_data.export_data(symbol, format, file_path)`
- [x] `historical_data.get_available_data_range(symbol, interval)`

## 2. Backtesting Engine (`tools/backtesting/`)

### Структура модуля:
```
tools/backtesting/
├── __init__.py
├── engine.py               # Основной движок бэктестинга
├── virtual_account.py      # Виртуальный торговый счет
├── position_manager.py     # Управление позициями в симуляции
├── performance_analyzer.py # Анализ результатов и метрики
├── visualization.py        # Графики и отчеты
└── strategy_runner.py      # Запуск стратегий на исторических данных
```

### Функциональность:
- [ ] Виртуальный торговый счет с балансом и историей операций
- [ ] Симуляция сделок с реалистичными комиссиями и проскальзыванием
- [ ] Управление множественными позициями
- [ ] Расчет метрик производительности (Sharpe ratio, максимальная просадка, Win Rate)
- [ ] Управление рисками в симуляции
- [ ] Генерация детальных отчетов и графиков
- [ ] Поддержка маржинальной торговли и левериджа

### MCP Tool Methods:
- [ ] `backtesting.create_virtual_account(initial_balance, leverage)`
- [ ] `backtesting.run_backtest(strategy_config, data, backtest_config)`
- [ ] `backtesting.get_performance_metrics(backtest_id)`
- [ ] `backtesting.generate_report(backtest_id, format)`
- [ ] `backtesting.compare_strategies(backtest_ids)`
- [ ] `backtesting.get_trades_history(backtest_id)`

## 3. Data Replay Tool (`tools/data_replay/`)

### Структура модуля:
```
tools/data_replay/
├── __init__.py
├── replay_engine.py        # Движок воспроизведения данных
├── time_controller.py      # Контроль времени симуляции
└── event_simulator.py      # Симуляция рыночных событий
```

### Функциональность:
- [ ] Пошаговое воспроизведение исторических данных
- [ ] Контроль скорости симуляции (1x, 10x, 100x, пауза)
- [ ] Имитация реального времени для тестирования торгового агента
- [ ] Возможность перемотки назад/вперед
- [ ] Симуляция рыночных событий и аномалий

### MCP Tool Methods:
- [ ] `data_replay.start_replay(data, speed_multiplier)`
- [ ] `data_replay.pause_replay()`
- [ ] `data_replay.resume_replay()`
- [ ] `data_replay.step_forward(steps)`
- [ ] `data_replay.jump_to_time(timestamp)`
- [ ] `data_replay.get_current_state()`

## 4. Strategy Testing Framework

### Функциональность:
- [ ] Базовый абстрактный класс для тестируемых стратегий
- [ ] Стандартизированный интерфейс для стратегий
- [ ] Метрики оценки производительности
- [ ] A/B тестирование разных параметров
- [ ] Оптимизация параметров стратегий (grid search, genetic algorithms)
- [ ] Валидация стратегий на out-of-sample данных

### Компоненты:
- [ ] `BaseStrategy` - базовый класс для стратегий
- [ ] `StrategyOptimizer` - оптимизация параметров
- [ ] `PerformanceMetrics` - расчет метрик
- [ ] `StrategyValidator` - валидация стратегий

## 5. Risk Analysis Tools

### Функциональность:
- [ ] Анализ корреляций между активами в портфеле
- [ ] Стресс-тестирование портфеля на исторических кризисах
- [ ] Анализ просадок и времени восстановления
- [ ] Monte Carlo симуляции для оценки рисков
- [ ] Value at Risk (VaR) и Conditional VaR расчеты
- [ ] Анализ волатильности и бета-коэффициентов

### Компоненты:
- [ ] `CorrelationAnalyzer` - анализ корреляций
- [ ] `StressTester` - стресс-тестирование
- [ ] `DrawdownAnalyzer` - анализ просадок
- [ ] `MonteCarloSimulator` - Monte Carlo симуляции

## 6. Reporting & Analytics

### Функциональность:
- [ ] HTML отчеты с интерактивными графиками (Plotly)
- [ ] Экспорт результатов в Excel/CSV
- [ ] Сравнение производительности разных стратегий
- [ ] Визуализация эквити кривой и просадок
- [ ] Календарные heat maps доходности
- [ ] Анализ распределения прибылей/убытков

### Компоненты:
- [ ] `HTMLReportGenerator` - HTML отчеты
- [ ] `ExcelExporter` - экспорт в Excel
- [ ] `ChartGenerator` - создание графиков
- [ ] `PerformanceComparator` - сравнение стратегий

## 7. Standalone тестирование

### Тестовые скрипты:
- [x] `test_historical_data.py` - Тест загрузки и кэширования исторических данных
- [ ] `test_backtesting.py` - Тест движка бэктестинга
- [ ] `test_data_replay.py` - Тест воспроизведения данных
- [ ] `test_strategy_framework.py` - Тест фреймворка стратегий
- [ ] `benchmark_performance.py` - Бенчмарк производительности системы

### Примеры использования:
- [ ] `examples/simple_backtest.py` - Простой пример бэктеста
- [ ] `examples/strategy_optimization.py` - Оптимизация стратегии
- [ ] `examples/portfolio_analysis.py` - Анализ портфеля
- [ ] `examples/risk_analysis.py` - Анализ рисков

## 8. Интеграция с существующей системой

### Конфигурация:
- [x] Расширить `config.json` секциями для исторических данных и бэктестинга
- [ ] Добавить настройки кэширования данных
- [ ] Настройки для параметров бэктестинга (комиссии, проскальзывание)

### CLI команды:
- [x] `python -m trading_ai_bot.tools.historical_data --symbol BTCUSDT --days 30`
- [ ] `python -m trading_ai_bot.tools.backtesting --config backtest_config.json`
- [ ] `python -m trading_ai_bot.tools.data_replay --data data.csv --speed 10x`

### TradingAgent интеграция:
- [ ] Режим симуляции для TradingAgent
- [ ] Переключение между live и backtest режимами
- [ ] Унифицированный интерфейс для получения данных

### MCP Server расширение:
- [ ] Регистрация новых инструментов в MCP сервере
- [ ] Обновление схем и документации
- [ ] Тестирование интеграции с Claude

## 9. Дополнительные улучшения

### Производительность:
- [ ] Использование numpy/pandas для быстрых вычислений
- [ ] Параллельная обработка данных
- [ ] Оптимизация работы с большими датасетами
- [ ] Кэширование промежуточных результатов

### Расширенная функциональность:
- [ ] Поддержка криптовалютных индексов
- [ ] Интеграция с другими биржами (через ccxt)
- [ ] Анализ новостного фона (sentiment analysis)
- [ ] Машинное обучение для предсказания цен

### Мониторинг и логирование:
- [ ] Детальное логирование операций бэктестинга
- [ ] Метрики производительности системы
- [ ] Алерты при аномальных результатах
- [ ] Dashboard для мониторинга бэктестов

## Приоритет реализации:

1. **Высокий приоритет:**
   - Historical Data Tool (основная функциональность)
   - Backtesting Engine (базовый движок)
   - Standalone тестирование

2. **Средний приоритет:**
   - Data Replay Tool
   - Strategy Testing Framework
   - Reporting & Analytics

3. **Низкий приоритет:**
   - Risk Analysis Tools (расширенные)
   - Дополнительные улучшения
   - ML интеграция

## Зависимости для установки:
- [x] `pandas` - работа с данными
- [x] `numpy` - численные вычисления
- [x] `sqlite3` - локальное кэширование
- [x] `plotly` - интерактивные графики
- [x] `openpyxl` - экспорт в Excel
- [x] `scipy` - статистические вычисления
- [ ] `scikit-learn` - машинное обучение (опционально)
