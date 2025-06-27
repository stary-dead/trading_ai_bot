import logging

class PromptBuilderTool:
    """
    Tool for creating AI prompts for market analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_enhanced_analysis_prompt(self, market_data_str: str) -> str:
        """Create enhanced analysis prompt for Claude"""
        
        prompt = f"""You are a professional cryptocurrency futures trader with 10+ years of experience in quantitative analysis and risk management. 

Your task is to analyze the comprehensive market data and provide a detailed trading recommendation for a medium-term position (1-8 hour holding period) focusing on scalping opportunities in futures markets.

{market_data_str}

ANALYSIS FRAMEWORK:
1. Technical Analysis Priority: RSI momentum, MACD signals, Bollinger Band position
2. Volume Analysis: VWAP relationship, volume trends, high-volume nodes
3. Support/Resistance: Key levels strength and proximity
4. Multi-timeframe Confirmation: Trend alignment across timeframes
5. Risk Management: Conservative position sizing and strict stop-losses

PROVIDE YOUR ANALYSIS IN STRICT JSON FORMAT ONLY:
{{
    "market_sentiment": "strongly_bullish/bullish/neutral/bearish/strongly_bearish",
    "confidence_score": 0.0-1.0,
    "recommended_action": "long/short/wait",
    "entry_strategy": {{
        "entry_price": number,
        "entry_condition": "market/limit order description",
        "position_size_percent": 1-10
    }},
    "risk_management": {{
        "stop_loss": number,
        "take_profit_1": number,
        "take_profit_2": number,
        "risk_reward_ratio": number,
        "max_loss_percent": number
    }},
    "technical_summary": {{
        "rsi_signal": "overbought/oversold/neutral",
        "macd_signal": "bullish/bearish/neutral", 
        "volume_confirmation": "strong/weak/neutral",
        "support_resistance_bias": "breakout/bounce/range"
    }},
    "timeframe_analysis": {{
        "short_term_bias": "bullish/bearish/neutral",
        "medium_term_bias": "bullish/bearish/neutral",
        "trend_alignment": true/false
    }},
    "key_levels": {{
        "immediate_resistance": number,
        "immediate_support": number,
        "vwap_level": number
    }},
    "market_structure": "trending_up/trending_down/consolidating/breakout_pending",
    "execution_notes": "specific entry and exit instructions",
    "reasoning": "comprehensive analysis explanation (max 300 words)"
}}

CRITICAL REQUIREMENTS:
- Only return valid JSON, no additional text
- Confidence > 0.8 only for very strong setups
- Stop-loss never more than 3% from entry
- Minimum risk:reward ratio of 1:2
- Position size max 10% of capital
- If analysis is unclear, set confidence < 0.5 and recommend "wait"
- Consider all technical indicators in combination, not individually"""

        return prompt
