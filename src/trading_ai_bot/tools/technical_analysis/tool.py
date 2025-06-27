"""
Technical Analysis Tool - MCP инструмент для технического анализа
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime


class TechnicalAnalysisTool:
    """
    MCP инструмент для продвинутого технического анализа с множественными индикаторами
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        MCP Tool: Рассчитать RSI (Relative Strength Index)
        
        Args:
            prices: Список цен закрытия
            period: Период для расчета (по умолчанию 14)
            
        Returns:
            Значение RSI от 0 до 100
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI if insufficient data
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """
        MCP Tool: Рассчитать MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Список цен закрытия
            
        Returns:
            Словарь с MACD, сигнальной линией и гистограммой
        """
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        df = pd.DataFrame({'close': prices})
        
        # Calculate EMAs
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': float(macd_line.iloc[-1]) if len(macd_line) > 0 else 0,
            'signal': float(signal_line.iloc[-1]) if len(signal_line) > 0 else 0,
            'histogram': float(histogram.iloc[-1]) if len(histogram) > 0 else 0
        }
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict:
        """
        MCP Tool: Рассчитать полосы Боллинджера
        
        Args:
            prices: Список цен закрытия
            period: Период для расчета (по умолчанию 20)
            std_dev: Количество стандартных отклонений (по умолчанию 2.0)
            
        Returns:
            Словарь с верхней, средней, нижней полосами и позицией цены
        """
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return {
                'upper': current_price * 1.02,
                'middle': current_price,
                'lower': current_price * 0.98,
                'position': 0.5  # Neutral position
            }
        
        df = pd.DataFrame({'close': prices})
        
        # Calculate middle band (SMA)
        middle = df['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = df['close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        current_price = prices[-1]
        upper_band = float(upper.iloc[-1])
        lower_band = float(lower.iloc[-1])
        middle_band = float(middle.iloc[-1])
        
        # Calculate position within bands (0 = lower band, 1 = upper band)
        band_width = upper_band - lower_band
        position = (current_price - lower_band) / band_width if band_width > 0 else 0.5
        
        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band,
            'position': position,
            'width': band_width / middle_band if middle_band > 0 else 0
        }
    
    def calculate_volume_profile(self, klines: List[Dict]) -> Dict:
        """
        MCP Tool: Рассчитать профиль объема и VWAP
        
        Args:
            klines: Список свечных данных
            
        Returns:
            Словарь с VWAP, трендом объема и узлами высокого объема
        """
        if not klines:
            return {'vwap': 0, 'volume_trend': 'neutral', 'high_volume_nodes': []}
        
        # Calculate VWAP (Volume Weighted Average Price)
        total_volume = 0
        total_price_volume = 0
        
        for candle in klines:
            typical_price = (candle['high'] + candle['low'] + candle['close']) / 3
            volume = candle['volume']
            total_price_volume += typical_price * volume
            total_volume += volume
        
        vwap = total_price_volume / total_volume if total_volume > 0 else 0
        
        # Analyze volume trend (last 10 vs previous 10 candles)
        if len(klines) >= 20:
            recent_volume = sum(c['volume'] for c in klines[-10:])
            previous_volume = sum(c['volume'] for c in klines[-20:-10])
            volume_ratio = recent_volume / previous_volume if previous_volume > 0 else 1
            
            if volume_ratio > 1.3:
                volume_trend = 'increasing'
            elif volume_ratio < 0.7:
                volume_trend = 'decreasing' 
            else:
                volume_trend = 'stable'
        else:
            volume_trend = 'insufficient_data'
        
        # Find high volume nodes (price levels with significant volume)
        price_volume_map = {}
        for candle in klines[-50:]:  # Last 50 candles
            price_level = round(candle['close'] / 100) * 100  # Round to nearest 100
            if price_level not in price_volume_map:
                price_volume_map[price_level] = 0
            price_volume_map[price_level] += candle['volume']
        
        # Get top 3 high volume nodes
        sorted_nodes = sorted(price_volume_map.items(), key=lambda x: x[1], reverse=True)
        high_volume_nodes = [price for price, volume in sorted_nodes[:3]]
        
        return {
            'vwap': vwap,
            'volume_trend': volume_trend,
            'high_volume_nodes': high_volume_nodes,
            'avg_volume': sum(c['volume'] for c in klines[-20:]) / min(20, len(klines))
        }
    
    def calculate_support_resistance(self, klines: List[Dict]) -> Dict:
        """
        MCP Tool: Рассчитать уровни поддержки и сопротивления
        
        Args:
            klines: Список свечных данных
            
        Returns:
            Словарь с уровнями поддержки, сопротивления и их силой
        """
        if len(klines) < 20:
            current_price = klines[-1]['close'] if klines else 0
            return {
                'resistance': current_price * 1.02,
                'support': current_price * 0.98,
                'strength': 'weak'
            }
        
        # Get highs and lows
        highs = [c['high'] for c in klines[-50:]]  # Last 50 candles
        lows = [c['low'] for c in klines[-50:]]
        
        # Find local maxima and minima
        resistance_levels = []
        support_levels = []
        
        for i in range(2, len(highs) - 2):
            # Local maximum (resistance)
            if highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i-2] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])
            
            # Local minimum (support)
            if lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i-2] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])
        
        current_price = klines[-1]['close']
        
        # Find nearest resistance above current price
        resistance = min([r for r in resistance_levels if r > current_price], default=current_price * 1.02)
        
        # Find nearest support below current price
        support = max([s for s in support_levels if s < current_price], default=current_price * 0.98)
        
        # Determine strength based on number of tests
        resistance_tests = sum(1 for h in highs if abs(h - resistance) / resistance < 0.005)
        support_tests = sum(1 for l in lows if abs(l - support) / support < 0.005)
        
        if resistance_tests >= 3 or support_tests >= 3:
            strength = 'strong'
        elif resistance_tests >= 2 or support_tests >= 2:
            strength = 'medium'
        else:
            strength = 'weak'
        
        return {
            'resistance': resistance,
            'support': support,
            'strength': strength,
            'resistance_tests': resistance_tests,
            'support_tests': support_tests
        }
    
    def analyze_multiple_timeframes(self, klines_data: Dict[str, List[Dict]]) -> Dict:
        """
        MCP Tool: Анализ нескольких таймфреймов для подтверждения тренда
        
        Args:
            klines_data: Словарь с данными для разных таймфреймов
            
        Returns:
            Анализ трендов по каждому таймфрейму и общий тренд
        """
        timeframe_analysis = {}
        
        for timeframe, klines in klines_data.items():
            if not klines or len(klines) < 10:
                continue
                
            closes = [c['close'] for c in klines]
            
            # Calculate basic trend indicators
            sma_short = sum(closes[-5:]) / 5 if len(closes) >= 5 else closes[-1]
            sma_long = sum(closes[-10:]) / 10 if len(closes) >= 10 else closes[-1]
            
            # Trend direction
            if sma_short > sma_long * 1.002:  # 0.2% threshold
                trend = 'bullish'
            elif sma_short < sma_long * 0.998:
                trend = 'bearish'
            else:
                trend = 'sideways'
            
            # Trend strength based on recent price action
            if len(closes) >= 5:
                price_change = (closes[-1] - closes[-5]) / closes[-5]
                if abs(price_change) > 0.02:  # 2% change
                    strength = 'strong'
                elif abs(price_change) > 0.01:  # 1% change
                    strength = 'medium'
                else:
                    strength = 'weak'
            else:
                strength = 'unknown'
            
            timeframe_analysis[timeframe] = {
                'trend': trend,
                'strength': strength,
                'sma_short': sma_short,
                'sma_long': sma_long
            }
        
        # Overall trend consensus
        trends = [analysis['trend'] for analysis in timeframe_analysis.values()]
        if trends.count('bullish') > trends.count('bearish'):
            overall_trend = 'bullish'
        elif trends.count('bearish') > trends.count('bullish'):
            overall_trend = 'bearish'
        else:
            overall_trend = 'mixed'
        
        return {
            'timeframes': timeframe_analysis,
            'overall_trend': overall_trend,
            'trend_agreement': len(set(trends)) == 1  # All timeframes agree
        }
    
    def comprehensive_analysis(self, market_data: Dict, multi_timeframe_data: Dict[str, List[Dict]] = None) -> Dict:
        """
        MCP Tool: Выполнить комплексный технический анализ
        
        Args:
            market_data: Основные рыночные данные
            multi_timeframe_data: Данные с нескольких таймфреймов (опционально)
            
        Returns:
            Полный технический анализ с интерпретацией сигналов
        """
        
        klines = market_data.get('klines', [])
        if not klines:
            return {}
        
        # Extract price data
        closes = [c['close'] for c in klines]
        highs = [c['high'] for c in klines]
        lows = [c['low'] for c in klines]
        
        # Calculate all indicators
        rsi = self.calculate_rsi(closes)
        macd = self.calculate_macd(closes)
        bollinger = self.calculate_bollinger_bands(closes)
        volume_analysis = self.calculate_volume_profile(klines)
        support_resistance = self.calculate_support_resistance(klines)
        
        # Multi-timeframe analysis
        if multi_timeframe_data:
            mtf_analysis = self.analyze_multiple_timeframes(multi_timeframe_data)
        else:
            mtf_analysis = {'overall_trend': 'unknown', 'trend_agreement': False}
        
        # Market structure analysis
        current_price = closes[-1]
        
        # Price position analysis
        price_vs_vwap = "above" if current_price > volume_analysis['vwap'] else "below"
        price_vs_bb = "upper" if bollinger['position'] > 0.8 else "lower" if bollinger['position'] < 0.2 else "middle"
        
        # Momentum analysis
        if rsi > 70:
            rsi_signal = "overbought"
        elif rsi < 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"
        
        if macd['histogram'] > 0:
            macd_signal = "bullish" if macd['macd'] > macd['signal'] else "strengthening"
        else:
            macd_signal = "bearish" if macd['macd'] < macd['signal'] else "weakening"
        
        return {
            'rsi': {
                'value': rsi,
                'signal': rsi_signal
            },
            'macd': {
                **macd,
                'signal_interpretation': macd_signal
            },
            'bollinger_bands': {
                **bollinger,
                'price_position': price_vs_bb
            },
            'volume': volume_analysis,
            'support_resistance': support_resistance,
            'price_analysis': {
                'vs_vwap': price_vs_vwap,
                'current': current_price
            },
            'multi_timeframe': mtf_analysis
        }
    
    async def analyze(self, market_data: Dict) -> Dict:
        """Async wrapper for comprehensive analysis"""
        return self.comprehensive_analysis(market_data)


# MCP Tool definitions для экспорта
MCP_TOOLS = {
    "calculate_rsi": {
        "description": "Рассчитать RSI (Relative Strength Index) для анализа momentum",
        "parameters": {
            "type": "object",
            "properties": {
                "prices": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Массив цен закрытия"
                },
                "period": {
                    "type": "integer",
                    "description": "Период для расчета RSI",
                    "default": 14
                }
            },
            "required": ["prices"]
        }
    },
    "calculate_macd": {
        "description": "Рассчитать MACD (Moving Average Convergence Divergence)",
        "parameters": {
            "type": "object",
            "properties": {
                "prices": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Массив цен закрытия"
                }
            },
            "required": ["prices"]
        }
    },
    "calculate_bollinger_bands": {
        "description": "Рассчитать полосы Боллинджера для анализа волатильности",
        "parameters": {
            "type": "object",
            "properties": {
                "prices": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Массив цен закрытия"
                },
                "period": {
                    "type": "integer",
                    "description": "Период для расчета средней линии",
                    "default": 20
                },
                "std_dev": {
                    "type": "number",
                    "description": "Количество стандартных отклонений",
                    "default": 2.0
                }
            },
            "required": ["prices"]
        }
    },
    "calculate_volume_profile": {
        "description": "Рассчитать профиль объема и VWAP",
        "parameters": {
            "type": "object",
            "properties": {
                "klines": {
                    "type": "array",
                    "description": "Массив свечных данных с полями high, low, close, volume"
                }
            },
            "required": ["klines"]
        }
    },
    "calculate_support_resistance": {
        "description": "Определить уровни поддержки и сопротивления",
        "parameters": {
            "type": "object",
            "properties": {
                "klines": {
                    "type": "array",
                    "description": "Массив свечных данных с полями high, low, close"
                }
            },
            "required": ["klines"]
        }
    },
    "analyze_multiple_timeframes": {
        "description": "Анализ нескольких таймфреймов для подтверждения тренда",
        "parameters": {
            "type": "object",
            "properties": {
                "klines_data": {
                    "type": "object",
                    "description": "Объект с данными для разных таймфреймов"
                }
            },
            "required": ["klines_data"]
        }
    },
    "comprehensive_analysis": {
        "description": "Выполнить полный технический анализ рынка",
        "parameters": {
            "type": "object",
            "properties": {
                "market_data": {
                    "type": "object",
                    "description": "Основные рыночные данные с klines"
                },
                "multi_timeframe_data": {
                    "type": "object",
                    "description": "Данные с нескольких таймфреймов (опционально)"
                }
            },
            "required": ["market_data"]
        }
    }
}
