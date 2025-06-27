"""
Data Loader - Загрузка данных из разных источников
"""
import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd


class DataLoader:
    """
    Загрузчик исторических данных с Binance
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get('base_url', 'https://fapi.binance.com')
        self.session = None
        self.max_klines_per_request = 500  # Ограничение Binance
        
    async def __aenter__(self):
        """Async context manager вход"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager выход"""
        if self.session:
            await self.session.close()
    
    async def load_klines(self, symbol: str, interval: str, start_time: Optional[datetime] = None, 
                         end_time: Optional[datetime] = None, limit: int = 500) -> Optional[List[Dict]]:
        """
        Загрузка свечных данных с Binance (до 500 свечей за раз)
        
        Args:
            symbol: Торговая пара (например, BTCUSDT)
            interval: Интервал (1m, 5m, 15m, 1h, 4h, 1d)
            start_time: Начальное время
            end_time: Конечное время
            limit: Количество свечей (макс 500)
            
        Returns:
            Список свечных данных или None при ошибке
        """
        try:
            url = f"{self.base_url}/fapi/v1/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": min(limit, self.max_klines_per_request)
            }
            
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Преобразуем в удобный формат
                    klines = []
                    for kline in data:
                        klines.append({
                            'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5])
                        })
                    
                    self.logger.info(f"Загружено {len(klines)} свечей для {symbol} ({interval})")
                    return klines
                else:
                    self.logger.error(f"Ошибка загрузки данных {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Исключение при загрузке данных {symbol}: {e}")
            return None
    
    async def load_data_range(self, symbol: str, interval: str, start_date: datetime, 
                             end_date: datetime) -> Optional[List[Dict]]:
        """
        Загрузка больших диапазонов данных по частям с автоматическим склеиванием
        
        Args:
            symbol: Торговая пара
            interval: Интервал
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Объединенный список свечных данных
        """
        try:
            all_klines = []
            current_start = start_date
            
            # Рассчитываем интервал времени для одного запроса
            interval_minutes = self._get_interval_minutes(interval)
            chunk_duration = timedelta(minutes=interval_minutes * self.max_klines_per_request)
            
            while current_start < end_date:
                current_end = min(current_start + chunk_duration, end_date)
                
                self.logger.info(f"Загрузка данных {symbol} с {current_start} по {current_end}")
                
                chunk_data = await self.load_klines(
                    symbol=symbol,
                    interval=interval,
                    start_time=current_start,
                    end_time=current_end,
                    limit=self.max_klines_per_request
                )
                
                if chunk_data:
                    all_klines.extend(chunk_data)
                    # Обновляем начальное время для следующего chunk
                    if chunk_data:
                        current_start = chunk_data[-1]['timestamp'] + timedelta(minutes=interval_minutes)
                    else:
                        break
                else:
                    self.logger.error(f"Не удалось загрузить chunk данных для {symbol}")
                    break
                
                # Пауза между запросами чтобы не превысить rate limit
                await asyncio.sleep(0.1)
            
            self.logger.info(f"Загружено всего {len(all_klines)} свечей для {symbol}")
            return all_klines
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке диапазона данных {symbol}: {e}")
            return None
    
    def _get_interval_minutes(self, interval: str) -> int:
        """
        Преобразует интервал в минуты
        
        Args:
            interval: Интервал (1m, 5m, 15m, 1h, 4h, 1d)
            
        Returns:
            Количество минут
        """
        interval_map = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        return interval_map.get(interval, 15)  # По умолчанию 15 минут
