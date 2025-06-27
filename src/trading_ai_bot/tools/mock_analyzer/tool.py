from datetime import datetime
from typing import Dict
import logging

class MockAnalyzerTool:
    """
    Tool for creating mock and fallback analysis when AI is unavailable
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_enhanced_mock_analysis(self, market_data: Dict, technical_analysis: Dict = None) -> Dict:
        """Create enhanced mock analysis for testing without Claude API"""
        
        current_price = market_data.get('current_price', 50000)
        change_24h = market_data.get('24h_change_percent', 0)
        
        # Use technical analysis if available
        if technical_analysis:
            rsi = technical_analysis.get('rsi', {}).get('value', 50)
            macd_signal = technical_analysis.get('macd', {}).get('signal_interpretation', 'neutral')
            bb_position = technical_analysis.get('bollinger_bands', {}).get('position', 0.5)
            volume_trend = technical_analysis.get('volume', {}).get('volume_trend', 'stable')
            overall_trend = technical_analysis.get('multi_timeframe', {}).get('overall_trend', 'mixed')
            
            # Enhanced logic based on technical indicators
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI signals
            if rsi > 60:
                bullish_signals += 1
            elif rsi < 40:
                bearish_signals += 1
            
            # MACD signals
            if macd_signal in ['bullish', 'strengthening']:
                bullish_signals += 1
            elif macd_signal in ['bearish', 'weakening']:
                bearish_signals += 1
            
            # Bollinger Band position
            if bb_position > 0.7:
                bearish_signals += 1  # Potentially overbought
            elif bb_position < 0.3:
                bullish_signals += 1  # Potentially oversold
            
            # Volume confirmation
            if volume_trend == 'increasing' and change_24h > 0:
                bullish_signals += 1
            elif volume_trend == 'increasing' and change_24h < 0:
                bearish_signals += 1
            
            # Multi-timeframe trend
            if overall_trend == 'bullish':
                bullish_signals += 2
            elif overall_trend == 'bearish':
                bearish_signals += 2
            
            # Determine sentiment and action
            if bullish_signals > bearish_signals + 1:
                sentiment = 'bullish'
                action = 'long'
                confidence = min(0.75, 0.5 + (bullish_signals - bearish_signals) * 0.1)
            elif bearish_signals > bullish_signals + 1:
                sentiment = 'bearish'
                action = 'short'
                confidence = min(0.75, 0.5 + (bearish_signals - bullish_signals) * 0.1)
            else:
                sentiment = 'neutral'
                action = 'wait'
                confidence = 0.4
        
        else:
            # Basic analysis without technical indicators
            if change_24h > 3:
                sentiment = 'bullish'
                action = 'long'
                confidence = 0.6
            elif change_24h < -3:
                sentiment = 'bearish'
                action = 'short'
                confidence = 0.6
            else:
                sentiment = 'neutral'
                action = 'wait'
                confidence = 0.4
        
        # Calculate prices based on action
        if action == 'long':
            entry_price = current_price
            stop_loss = current_price * 0.98
            take_profit_1 = current_price * 1.04
            take_profit_2 = current_price * 1.06
        elif action == 'short':
            entry_price = current_price
            stop_loss = current_price * 1.02
            take_profit_1 = current_price * 0.96
            take_profit_2 = current_price * 0.94
        else:
            entry_price = current_price
            stop_loss = current_price * 0.985
            take_profit_1 = current_price * 1.03
            take_profit_2 = current_price * 1.05
        
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit_1 - entry_price)
        risk_reward = reward / risk if risk > 0 else 2.0
        
        return {
            'market_sentiment': sentiment,
            'confidence_score': confidence,
            'recommended_action': action,
            'entry_strategy': {
                'entry_price': entry_price,
                'entry_condition': 'market order at current price',
                'position_size_percent': 3 if confidence > 0.6 else 2
            },
            'risk_management': {
                'stop_loss': stop_loss,
                'take_profit_1': take_profit_1,
                'take_profit_2': take_profit_2,
                'risk_reward_ratio': risk_reward,
                'max_loss_percent': 2.0
            },
            'technical_summary': {
                'rsi_signal': technical_analysis.get('rsi', {}).get('signal', 'neutral') if technical_analysis else 'neutral',
                'macd_signal': technical_analysis.get('macd', {}).get('signal_interpretation', 'neutral') if technical_analysis else 'neutral',
                'volume_confirmation': technical_analysis.get('volume', {}).get('volume_trend', 'neutral') if technical_analysis else 'neutral',
                'support_resistance_bias': 'range'
            },
            'timeframe_analysis': {
                'short_term_bias': sentiment,
                'medium_term_bias': technical_analysis.get('multi_timeframe', {}).get('overall_trend', 'neutral') if technical_analysis else 'neutral',
                'trend_alignment': technical_analysis.get('multi_timeframe', {}).get('trend_agreement', False) if technical_analysis else False
            },
            'key_levels': {
                'immediate_resistance': current_price * 1.02,
                'immediate_support': current_price * 0.98,
                'vwap_level': technical_analysis.get('volume', {}).get('vwap', current_price) if technical_analysis else current_price
            },
            'market_structure': 'consolidating',
            'execution_notes': f'Mock analysis based on {sentiment} sentiment. Entry at market price with tight stops.',
            'reasoning': f'Enhanced mock analysis: {sentiment} sentiment based on technical indicators and 24h change ({change_24h:.2f}%). Confidence: {confidence:.2f}',
            'timestamp': datetime.now().isoformat(),
            'analyzer': 'enhanced_mock',
            'symbol': market_data.get('symbol', 'UNKNOWN')
        }
    
    def create_fallback_analysis(self, market_data: Dict) -> Dict:
        """Create fallback analysis in case of errors"""
        
        current_price = market_data.get('current_price', 50000)
        
        return {
            'market_sentiment': 'neutral',
            'confidence_score': 0.2,
            'recommended_action': 'wait',
            'entry_strategy': {
                'entry_price': current_price,
                'entry_condition': 'wait for clearer signals',
                'position_size_percent': 1
            },
            'risk_management': {
                'stop_loss': current_price * 0.98,
                'take_profit_1': current_price * 1.02,
                'take_profit_2': current_price * 1.04,
                'risk_reward_ratio': 2.0,
                'max_loss_percent': 2.0
            },
            'technical_summary': {
                'rsi_signal': 'neutral',
                'macd_signal': 'neutral',
                'volume_confirmation': 'neutral',
                'support_resistance_bias': 'range'
            },
            'timeframe_analysis': {
                'short_term_bias': 'neutral',
                'medium_term_bias': 'neutral',
                'trend_alignment': False
            },
            'key_levels': {
                'immediate_resistance': current_price * 1.02,
                'immediate_support': current_price * 0.98,
                'vwap_level': current_price
            },
            'market_structure': 'consolidating',
            'execution_notes': 'Insufficient data for reliable analysis. Wait for clearer market signals.',
            'reasoning': 'Fallback analysis due to data errors or API issues. Conservative approach recommended.',
            'timestamp': datetime.now().isoformat(),
            'analyzer': 'fallback',
            'symbol': market_data.get('symbol', 'UNKNOWN')
        }
