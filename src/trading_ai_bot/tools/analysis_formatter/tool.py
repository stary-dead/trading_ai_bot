from datetime import datetime
from typing import Dict, List
import logging

class AnalysisFormatterTool:
    """
    Tool for formatting market and technical analysis data for AI consumption
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_comprehensive_market_data(self, market_data: Dict, technical_analysis: Dict = None) -> str:
        """Format comprehensive market data for Claude analysis"""
        
        # Extract key data
        symbol = market_data.get('symbol', 'UNKNOWN')
        current_price = market_data.get('current_price', 0)
        change_24h = market_data.get('24h_change_percent', 0)
        volume_24h = market_data.get('24h_volume', 0)
        high_24h = market_data.get('24h_high', 0)
        low_24h = market_data.get('24h_low', 0)
        
        formatted_data = f"""
🚀 COMPREHENSIVE MARKET ANALYSIS - {symbol}
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

📊 CURRENT MARKET STATE:
• Current Price: ${current_price:,.2f}
• 24h Change: {change_24h:+.2f}%
• 24h Volume: {volume_24h:,.0f} USDT
• 24h Range: ${low_24h:,.2f} - ${high_24h:,.2f}
• Daily Range: {((high_24h - low_24h) / low_24h * 100):.2f}%
"""

        # Add technical analysis if available
        if technical_analysis:
            formatted_data += self.format_technical_indicators(technical_analysis)
            formatted_data += self.format_volume_analysis(technical_analysis)
            formatted_data += self.format_support_resistance(technical_analysis)
            formatted_data += self.format_multi_timeframe_analysis(technical_analysis)
        
        # Add recent candles
        klines = market_data.get('klines', [])
        if klines:
            formatted_data += self.format_recent_candles(klines[-15:])  # Last 15 candles
        
        return formatted_data
    
    def format_technical_indicators(self, analysis: Dict) -> str:
        """Format technical indicators section"""
        
        rsi_data = analysis.get('rsi', {})
        macd_data = analysis.get('macd', {})
        bb_data = analysis.get('bollinger_bands', {})
        
        section = f"""
🔧 TECHNICAL INDICATORS:
• RSI(14): {rsi_data.get('value', 0):.1f} ({rsi_data.get('signal', 'neutral').upper()})
• MACD: {macd_data.get('macd', 0):.4f}
  - Signal: {macd_data.get('signal', 0):.4f}
  - Histogram: {macd_data.get('histogram', 0):.4f}
  - Interpretation: {macd_data.get('signal_interpretation', 'neutral').upper()}

📈 BOLLINGER BANDS:
• Upper Band: ${bb_data.get('upper', 0):.2f}
• Middle Band (SMA20): ${bb_data.get('middle', 0):.2f}
• Lower Band: ${bb_data.get('lower', 0):.2f}
• Price Position: {bb_data.get('price_position', 'unknown').upper()} band
• Band Width: {(bb_data.get('width', 0) * 100):.2f}% (volatility indicator)
"""
        return section
    
    def format_volume_analysis(self, analysis: Dict) -> str:
        """Format volume analysis section"""
        
        volume_data = analysis.get('volume', {})
        
        section = f"""
📊 VOLUME ANALYSIS:
• VWAP: ${volume_data.get('vwap', 0):.2f}
• Volume Trend: {volume_data.get('volume_trend', 'unknown').upper()}
• Average Volume: {volume_data.get('avg_volume', 0):,.0f}
• High Volume Nodes: {', '.join([f'${level:,.0f}' for level in volume_data.get('high_volume_nodes', [])])}
"""
        return section
    
    def format_support_resistance(self, analysis: Dict) -> str:
        """Format support and resistance section"""
        
        sr_data = analysis.get('support_resistance', {})
        price_data = analysis.get('price_analysis', {})
        current_price = price_data.get('current', 0)
        
        section = f"""
🎯 SUPPORT & RESISTANCE:
• Resistance: ${sr_data.get('resistance', 0):.2f} (Strength: {sr_data.get('strength', 'unknown').upper()})
• Support: ${sr_data.get('support', 0):.2f} (Strength: {sr_data.get('strength', 'unknown').upper()})
• Distance to Resistance: {((sr_data.get('resistance', 0) - current_price) / current_price * 100):+.2f}%
• Distance to Support: {((sr_data.get('support', 0) - current_price) / current_price * 100):+.2f}%
• Price vs VWAP: {price_data.get('vs_vwap', 'unknown').upper()}
"""
        return section
    
    def format_multi_timeframe_analysis(self, analysis: Dict) -> str:
        """Format multi-timeframe analysis section"""
        
        mtf_data = analysis.get('multi_timeframe', {})
        timeframes = mtf_data.get('timeframes', {})
        
        section = f"""
⏰ MULTI-TIMEFRAME ANALYSIS:
• Overall Trend: {mtf_data.get('overall_trend', 'unknown').upper()}
• Trend Agreement: {'YES' if mtf_data.get('trend_agreement', False) else 'NO'}

"""
        
        for tf, tf_data in timeframes.items():
            section += f"  {tf}: {tf_data.get('trend', 'unknown').upper()} ({tf_data.get('strength', 'unknown')} strength)\n"
        
        return section
    
    def format_recent_candles(self, klines: List[Dict]) -> str:
        """Format recent candles data"""
        
        section = f"""
🕯️ RECENT PRICE ACTION (Last {len(klines)} candles):
"""
        
        for i, candle in enumerate(klines[-10:]):  # Show last 10 candles
            time_str = candle['timestamp'].strftime('%H:%M')
            body_color = "🟢" if candle['close'] > candle['open'] else "🔴"
            body_size = abs(candle['close'] - candle['open'])
            wick_upper = candle['high'] - max(candle['open'], candle['close'])
            wick_lower = min(candle['open'], candle['close']) - candle['low']
            
            section += f"• {time_str} {body_color} O:{candle['open']:.2f} H:{candle['high']:.2f} L:{candle['low']:.2f} C:{candle['close']:.2f} V:{candle['volume']:.0f}\n"
        
        return section
