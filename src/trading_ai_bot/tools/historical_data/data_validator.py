"""
Data Validator - Валидация исторических данных
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class DataValidator:
    """
    Валидатор для проверки целостности исторических данных
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_data(self, data: List[Dict], symbol: str = "", interval: str = "") -> Dict:
        """
        Валидация данных (проверка пропусков, дубликатов)
        
        Args:
            data: Список свечных данных
            symbol: Торговая пара (для логирования)
            interval: Интервал (для логирования)
            
        Returns:
            Словарь с результатами валидации
        """
        result = {
            'is_valid': True,
            'total_count': len(data),
            'duplicates': [],
            'gaps': [],
            'invalid_prices': [],
            'invalid_volumes': [],
            'errors': []
        }
        
        try:
            if not data:
                result['is_valid'] = False
                result['errors'].append('Данные пустые')
                return result
            
            # Проверяем дубликаты по timestamp
            result['duplicates'] = self._check_duplicates(data)
            
            # Проверяем пропуски во времени
            result['gaps'] = self._check_time_gaps(data, interval)
            
            # Проверяем корректность цен
            result['invalid_prices'] = self._check_price_validity(data)
            
            # Проверяем корректность объемов
            result['invalid_volumes'] = self._check_volume_validity(data)
            
            # Определяем общую валидность
            if (result['duplicates'] or result['gaps'] or 
                result['invalid_prices'] or result['invalid_volumes']):
                result['is_valid'] = False
            
            # Логируем результаты
            if result['is_valid']:
                self.logger.info(f"Данные {symbol} ({interval}) прошли валидацию успешно")
            else:
                issues = []
                if result['duplicates']:
                    issues.append(f"{len(result['duplicates'])} дубликатов")
                if result['gaps']:
                    issues.append(f"{len(result['gaps'])} пропусков")
                if result['invalid_prices']:
                    issues.append(f"{len(result['invalid_prices'])} некорректных цен")
                if result['invalid_volumes']:
                    issues.append(f"{len(result['invalid_volumes'])} некорректных объемов")
                
                self.logger.warning(f"Данные {symbol} ({interval}) содержат ошибки: {', '.join(issues)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации данных {symbol}: {e}")
            result['is_valid'] = False
            result['errors'].append(f"Исключение при валидации: {e}")
            return result
    
    def _check_duplicates(self, data: List[Dict]) -> List[Dict]:
        """
        Проверка дубликатов по timestamp
        
        Args:
            data: Список свечных данных
            
        Returns:
            Список дубликатов
        """
        seen_timestamps = set()
        duplicates = []
        
        for i, item in enumerate(data):
            timestamp = item['timestamp']
            if timestamp in seen_timestamps:
                duplicates.append({
                    'index': i,
                    'timestamp': timestamp,
                    'data': item
                })
            else:
                seen_timestamps.add(timestamp)
        
        return duplicates
    
    def _check_time_gaps(self, data: List[Dict], interval: str) -> List[Dict]:
        """
        Проверка пропусков во времени
        
        Args:
            data: Список свечных данных
            interval: Интервал данных
            
        Returns:
            Список найденных пропусков
        """
        if len(data) < 2:
            return []
        
        # Получаем ожидаемую разность во времени
        expected_delta = self._get_interval_timedelta(interval)
        if not expected_delta:
            return []  # Неизвестный интервал
        
        gaps = []
        
        # Сортируем данные по времени
        sorted_data = sorted(data, key=lambda x: x['timestamp'])
        
        for i in range(1, len(sorted_data)):
            current_time = sorted_data[i]['timestamp']
            previous_time = sorted_data[i-1]['timestamp']
            actual_delta = current_time - previous_time
            
            # Проверяем, есть ли значительный пропуск
            if actual_delta > expected_delta * 1.5:  # Допускаем 50% отклонение
                missing_periods = int(actual_delta.total_seconds() / expected_delta.total_seconds()) - 1
                gaps.append({
                    'previous_timestamp': previous_time,
                    'current_timestamp': current_time,
                    'expected_delta': expected_delta,
                    'actual_delta': actual_delta,
                    'missing_periods': missing_periods
                })
        
        return gaps
    
    def _check_price_validity(self, data: List[Dict]) -> List[Dict]:
        """
        Проверка корректности цен (OHLC логика)
        
        Args:
            data: Список свечных данных
            
        Returns:
            Список некорректных цен
        """
        invalid_prices = []
        
        for i, item in enumerate(data):
            errors = []
            
            # Проверяем, что все цены положительные
            if not all(price > 0 for price in [item['open'], item['high'], item['low'], item['close']]):
                errors.append('Отрицательные или нулевые цены')
            
            # Проверяем OHLC логику
            if item['high'] < max(item['open'], item['close']):
                errors.append('High меньше максимума из Open/Close')
            
            if item['low'] > min(item['open'], item['close']):
                errors.append('Low больше минимума из Open/Close')
            
            if item['high'] < item['low']:
                errors.append('High меньше Low')
            
            # Проверяем на аномальные движения цены (более 50% за период)
            if i > 0:
                prev_close = data[i-1]['close']
                price_change = abs(item['close'] - prev_close) / prev_close
                if price_change > 0.5:  # 50% изменение
                    errors.append(f'Аномальное изменение цены: {price_change:.2%}')
            
            if errors:
                invalid_prices.append({
                    'index': i,
                    'timestamp': item['timestamp'],
                    'data': item,
                    'errors': errors
                })
        
        return invalid_prices
    
    def _check_volume_validity(self, data: List[Dict]) -> List[Dict]:
        """
        Проверка корректности объемов
        
        Args:
            data: Список свечных данных
            
        Returns:
            Список некорректных объемов
        """
        invalid_volumes = []
        
        if not data:
            return invalid_volumes
        
        # Рассчитываем медианный объем для сравнения
        volumes = [item['volume'] for item in data if item['volume'] > 0]
        if not volumes:
            return invalid_volumes
        
        median_volume = sorted(volumes)[len(volumes) // 2]
        
        for i, item in enumerate(data):
            errors = []
            
            # Проверяем на отрицательный объем
            if item['volume'] < 0:
                errors.append('Отрицательный объем')
            
            # Проверяем на аномально высокий объем (более чем в 100 раз выше медианы)
            if item['volume'] > median_volume * 100:
                errors.append(f'Аномально высокий объем: {item["volume"]:.2f} (медиана: {median_volume:.2f})')
            
            if errors:
                invalid_volumes.append({
                    'index': i,
                    'timestamp': item['timestamp'],
                    'volume': item['volume'],
                    'errors': errors
                })
        
        return invalid_volumes
    
    def _get_interval_timedelta(self, interval: str) -> Optional[timedelta]:
        """
        Преобразует интервал в timedelta
        
        Args:
            interval: Интервал (1m, 5m, 15m, 1h, 4h, 1d)
            
        Returns:
            timedelta объект или None
        """
        interval_map = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '1h': timedelta(hours=1),
            '4h': timedelta(hours=4),
            '1d': timedelta(days=1)
        }
        return interval_map.get(interval)
