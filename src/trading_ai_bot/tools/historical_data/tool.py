"""
Historical Data Tool - основной MCP инструмент
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .data_loader import DataLoader
from .data_storage import DataStorage
from .data_validator import DataValidator


class HistoricalDataTool:
    """
    MCP инструмент для работы с историческими данными
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Инициализируем компоненты
        self.data_loader = DataLoader(config.get('exchange', {}))
        self.data_storage = DataStorage(config.get('historical_data', {}))
        self.data_validator = DataValidator(config.get('historical_data', {}))
        
        # Поддерживаемые форматы экспорта
        self.supported_formats = ['csv', 'json']
        
        # Поддерживаемые интервалы
        self.supported_intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
    
    async def __aenter__(self):
        """Async context manager вход"""
        await self.data_loader.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager выход"""
        await self.data_loader.__aexit__(exc_type, exc_val, exc_tb)
    
    async def load_data(self, symbol: str, start_date: str, end_date: str, 
                       interval: str = '15m') -> Dict[str, Any]:
        """
        MCP Method: Загрузка исторических данных
        
        Args:
            symbol: Торговая пара (например, BTCUSDT)
            start_date: Начальная дата (ISO формат: 2024-01-01)
            end_date: Конечная дата (ISO формат: 2024-01-31)
            interval: Интервал (1m, 5m, 15m, 1h, 4h, 1d)
            
        Returns:
            Словарь с результатами загрузки
        """
        try:
            # Валидация параметров
            if interval not in self.supported_intervals:
                return {
                    'success': False,
                    'error': f'Неподдерживаемый интервал: {interval}. Поддерживаемые: {self.supported_intervals}'
                }
            
            # Парсим даты
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            if start_dt >= end_dt:
                return {
                    'success': False,
                    'error': 'Начальная дата должна быть меньше конечной'
                }
            
            self.logger.info(f"Загрузка данных {symbol} с {start_date} по {end_date} ({interval})")
            
            # Загружаем данные
            data = await self.data_loader.load_data_range(symbol, interval, start_dt, end_dt)
            
            if not data:
                return {
                    'success': False,
                    'error': 'Не удалось загрузить данные'
                }
            
            # Валидируем данные
            validation_result = self.data_validator.validate_data(data, symbol, interval)
            
            # Кэшируем данные
            cache_success = self.data_storage.cache_data(symbol, interval, data)
            
            return {
                'success': True,
                'symbol': symbol,
                'interval': interval,
                'start_date': start_date,
                'end_date': end_date,
                'records_count': len(data),
                'validation': validation_result,
                'cached': cache_success,
                'first_record': data[0] if data else None,
                'last_record': data[-1] if data else None
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cache_data(self, symbol: str, data: List[Dict], interval: str = '15m') -> Dict[str, Any]:
        """
        MCP Method: Кэширование данных
        
        Args:
            symbol: Торговая пара
            data: Список свечных данных
            interval: Интервал
            
        Returns:
            Результат кэширования
        """
        try:
            # Валидируем данные перед кэшированием
            validation_result = self.data_validator.validate_data(data, symbol, interval)
            
            # Кэшируем данные
            cache_success = self.data_storage.cache_data(symbol, interval, data)
            
            return {
                'success': cache_success,
                'symbol': symbol,
                'interval': interval,
                'records_count': len(data),
                'validation': validation_result
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка кэширования данных {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cached_data(self, symbol: str, start_date: str, end_date: str, 
                       interval: str = '15m') -> Dict[str, Any]:
        """
        MCP Method: Получение кэшированных данных
        
        Args:
            symbol: Торговая пара
            start_date: Начальная дата (ISO формат)
            end_date: Конечная дата (ISO формат)
            interval: Интервал
            
        Returns:
            Кэшированные данные
        """
        try:
            # Парсим даты
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # Получаем данные из кэша
            data = self.data_storage.get_cached_data(symbol, interval, start_dt, end_dt)
            
            if not data:
                return {
                    'success': False,
                    'message': 'Нет кэшированных данных для указанного периода'
                }
            
            return {
                'success': True,
                'symbol': symbol,
                'interval': interval,
                'start_date': start_date,
                'end_date': end_date,
                'records_count': len(data),
                'data': data,
                'first_record': data[0],
                'last_record': data[-1]
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения кэшированных данных {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_data(self, data: List[Dict], symbol: str = "", interval: str = "") -> Dict[str, Any]:
        """
        MCP Method: Валидация данных
        
        Args:
            data: Список свечных данных
            symbol: Торговая пара (опционально)
            interval: Интервал (опционально)
            
        Returns:
            Результаты валидации
        """
        try:
            validation_result = self.data_validator.validate_data(data, symbol, interval)
            
            return {
                'success': True,
                'validation_result': validation_result
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации данных: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_data(self, symbol: str, format: str, file_path: str, 
                   interval: str = '15m', start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        MCP Method: Экспорт данных в файл
        
        Args:
            symbol: Торговая пара
            format: Формат файла (csv, json)
            file_path: Путь к файлу
            interval: Интервал
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            
        Returns:
            Результат экспорта
        """
        try:
            if format not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Неподдерживаемый формат: {format}. Поддерживаемые: {self.supported_formats}'
                }
            
            # Парсим даты если указаны
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            # Создаем директорию если не существует
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Экспортируем в зависимости от формата
            if format == 'csv':
                success = self.data_storage.export_to_csv(symbol, interval, file_path, start_dt, end_dt)
            elif format == 'json':
                success = self.data_storage.export_to_json(symbol, interval, file_path, start_dt, end_dt)
            else:
                return {
                    'success': False,
                    'error': f'Неподдерживаемый формат: {format}'
                }
            
            return {
                'success': success,
                'symbol': symbol,
                'interval': interval,
                'format': format,
                'file_path': file_path,
                'start_date': start_date,
                'end_date': end_date
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта данных {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_data_range(self, symbol: str, interval: str = '15m') -> Dict[str, Any]:
        """
        MCP Method: Получение доступного диапазона данных в кэше
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            
        Returns:
            Информация о доступном диапазоне данных
        """
        try:
            range_info = self.data_storage.get_available_data_range(symbol, interval)
            
            if not range_info:
                return {
                    'success': False,
                    'message': 'Нет кэшированных данных для указанного символа и интервала'
                }
            
            return {
                'success': True,
                'symbol': symbol,
                'interval': interval,
                'min_date': range_info['min_date'].isoformat(),
                'max_date': range_info['max_date'].isoformat(),
                'records_count': range_info['count']
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения диапазона данных {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
