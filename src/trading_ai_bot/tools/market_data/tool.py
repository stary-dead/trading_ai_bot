"""
Market Data Tool - MCP инструмент для получения рыночных данных
"""
import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd


class MarketDataTool:
    """
    MCP инструмент для получения рыночных данных с Binance Futures API
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get('base_url', 'https://fapi.binance.com')
        self.session = None
        
    async def __aenter__(self):
        """Async context manager вход"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager выход"""
        if self.session:
            await self.session.close()
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """
        MCP Tool: Получить текущую цену символа
        
        Args:
            symbol: Торговая пара (например, BTCUSDT)
            
        Returns:
            Текущая цена или None при ошибке
        """
        try:
            url = f"{self.base_url}/fapi/v1/ticker/price"
            params = {"symbol": symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data['price'])
                    self.logger.info(f"Текущая цена {symbol}: {price}")
                    return price
                else:
                    self.logger.error(f"Ошибка получения цены {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Исключение при получении цены {symbol}: {e}")
            return None
    
    async def get_klines(self, symbol: str, interval: str = '15m', limit: int = 100) -> Optional[List[Dict]]:
        """
        MCP Tool: Получить свечные данные
        
        Args:
            symbol: Торговая пара (например, BTCUSDT)
            interval: Интервал (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Количество свечей (макс 1000)
            
        Returns:
            Список свечных данных или None при ошибке
        """
        try:
            url = f"{self.base_url}/fapi/v1/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
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
                    
                    self.logger.info(f"Получено {len(klines)} свечей для {symbol}")
                    return klines
                else:
                    self.logger.error(f"Ошибка получения свечей {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Исключение при получении свечей {symbol}: {e}")
            return None
    
    async def get_24hr_ticker(self, symbol: str) -> Optional[Dict]:
        """
        MCP Tool: Получить 24-часовую статистику по символу
        
        Args:
            symbol: Торговая пара
            
        Returns:
            Словарь с 24-часовой статистикой или None при ошибке
        """
        try:
            url = f"{self.base_url}/fapi/v1/ticker/24hr"
            params = {"symbol": symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    ticker = {
                        'symbol': data['symbol'],
                        'price_change': float(data['priceChange']),
                        'price_change_percent': float(data['priceChangePercent']),
                        'last_price': float(data['lastPrice']),
                        'volume': float(data['volume']),
                        'high_price': float(data['highPrice']),
                        'low_price': float(data['lowPrice'])
                    }
                    
                    self.logger.info(f"24h статистика для {symbol}: изменение {ticker['price_change_percent']:.2f}%")
                    return ticker
                else:
                    self.logger.error(f"Ошибка получения 24h статистики {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Исключение при получении 24h статистики {symbol}: {e}")
            return None
    
    async def get_multi_timeframe_data(self, symbol: str, timeframes: List[str] = None) -> Dict[str, List[Dict]]:
        """
        MCP Tool: Получить данные с нескольких таймфреймов для анализа
        
        Args:
            symbol: Торговая пара
            timeframes: Список таймфреймов ['5m', '15m', '1h', '4h']
            
        Returns:
            Словарь с данными для каждого таймфрейма
        """
        if timeframes is None:
            timeframes = ['5m', '15m', '1h', '4h']
        
        try:
            multi_data = {}
            
            # Определяем количество свечей для каждого таймфрейма
            limits = {
                '1m': 100, '3m': 100, '5m': 100,
                '15m': 100, '30m': 80, '1h': 60,
                '2h': 50, '4h': 40, '6h': 30,
                '8h': 25, '12h': 20, '1d': 15
            }
            
            # Получаем данные параллельно
            tasks = []
            for tf in timeframes:
                limit = limits.get(tf, 50)
                task = self.get_klines(symbol, tf, limit)
                tasks.append((tf, task))
            
            # Выполняем все запросы
            for tf, task in tasks:
                klines = await task
                if klines:
                    multi_data[tf] = klines
                    self.logger.info(f"Получено {len(klines)} свечей для {symbol} {tf}")
                else:
                    self.logger.warning(f"Не удалось получить данные для {symbol} {tf}")
            
            return multi_data
            
        except Exception as e:
            self.logger.error(f"Ошибка получения мультитаймфрейм данных для {symbol}: {e}")
            return {}
    
    async def get_market_data(self, symbol: str, include_multi_timeframe: bool = False) -> Optional[Dict]:
        """
        MCP Tool: Получить полные данные рынка для анализа
        
        Args:
            symbol: Торговая пара
            include_multi_timeframe: Включить данные с нескольких таймфреймов
            
        Returns:
            Полные рыночные данные или None при ошибке
        """
        try:
            # Получаем основные данные параллельно
            tasks = [
                self.get_current_price(symbol),
                self.get_klines(symbol, '15m', 100),
                self.get_24hr_ticker(symbol)
            ]
            
            # Если нужны мультитаймфрейм данные, добавляем их
            if include_multi_timeframe:
                tasks.append(self.get_multi_timeframe_data(symbol))
            else:
                tasks.append(asyncio.create_task(asyncio.sleep(0, result={})))  # Пустая задача
            
            current_price, klines, ticker_24h, multi_tf_data = await asyncio.gather(*tasks)
            
            if not all([current_price, klines, ticker_24h]):
                self.logger.error(f"Не удалось получить все данные для {symbol}")
                return None
            
            # Рассчитываем дополнительные метрики
            recent_prices = [k['close'] for k in klines[-20:]]  # Последние 20 свечей
            sma_20 = sum(recent_prices) / len(recent_prices)
            
            market_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'current_price': current_price,
                'sma_20': sma_20,
                'price_above_sma': current_price > sma_20,
                'klines': klines,
                '24h_change_percent': ticker_24h['price_change_percent'],
                '24h_volume': ticker_24h['volume'],
                '24h_high': ticker_24h['high_price'],
                '24h_low': ticker_24h['low_price']
            }
            
            # Добавляем мультитаймфрейм данные если запрошены
            if include_multi_timeframe and multi_tf_data:
                market_data['multi_timeframe'] = multi_tf_data
            
            self.logger.info(f"Полные рыночные данные получены для {symbol}")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Ошибка получения рыночных данных для {symbol}: {e}")
            return None


# MCP Tool definitions для экспорта
MCP_TOOLS = {
    "get_current_price": {
        "description": "Получить текущую цену торговой пары",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Торговая пара (например, BTCUSDT)"
                }
            },
            "required": ["symbol"]
        }
    },
    "get_klines": {
        "description": "Получить свечные данные для технического анализа",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Торговая пара (например, BTCUSDT)"
                },
                "interval": {
                    "type": "string",
                    "description": "Интервал свечей (1m, 5m, 15m, 1h, 4h, 1d)",
                    "default": "15m"
                },
                "limit": {
                    "type": "integer",
                    "description": "Количество свечей (макс 1000)",
                    "default": 100
                }
            },
            "required": ["symbol"]
        }
    },
    "get_24hr_ticker": {
        "description": "Получить 24-часовую статистику по торговой паре",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Торговая пара (например, BTCUSDT)"
                }
            },
            "required": ["symbol"]
        }
    },
    "get_multi_timeframe_data": {
        "description": "Получить данные с нескольких таймфреймов для комплексного анализа",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Торговая пара (например, BTCUSDT)"
                },
                "timeframes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список таймфреймов для анализа",
                    "default": ["5m", "15m", "1h", "4h"]
                }
            },
            "required": ["symbol"]
        }
    },
    "get_market_data": {
        "description": "Получить полные рыночные данные для анализа",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Торговая пара (например, BTCUSDT)"
                },
                "include_multi_timeframe": {
                    "type": "boolean",
                    "description": "Включить данные с нескольких таймфреймов",
                    "default": False
                }
            },
            "required": ["symbol"]
        }
    }
}
