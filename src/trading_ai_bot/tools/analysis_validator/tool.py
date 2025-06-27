from datetime import datetime
from typing import Dict
import logging

class AnalysisValidatorTool:
    """
    Tool for validating and correcting trading analysis results
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_enhanced_analysis(self, analysis: Dict, market_data: Dict) -> Dict:
        """Validate and correct enhanced analysis from Claude"""
        
        current_price = market_data.get('current_price', 50000)
        
        # Check required fields
        required_fields = [
            'market_sentiment', 'confidence_score', 'recommended_action',
            'entry_strategy', 'risk_management', 'reasoning'
        ]
        
        for field in required_fields:
            if field not in analysis:
                self.logger.warning(f"Missing field {field} in Claude analysis")
                analysis[field] = self.get_enhanced_default_value(field, current_price)
        
        # Validate confidence score
        if not 0 <= analysis.get('confidence_score', 0) <= 1:
            analysis['confidence_score'] = max(0, min(1, analysis.get('confidence_score', 0.5)))
        
        # Validate entry strategy
        entry_strategy = analysis.get('entry_strategy', {})
        if 'entry_price' not in entry_strategy:
            entry_strategy['entry_price'] = current_price
        
        entry_price = entry_strategy['entry_price']
        if abs(entry_price - current_price) > current_price * 0.05:  # Max 5% from current price
            entry_strategy['entry_price'] = current_price
        
        # Validate risk management
        risk_mgmt = analysis.get('risk_management', {})
        if 'stop_loss' not in risk_mgmt:
            risk_mgmt['stop_loss'] = current_price * 0.98
        
        # Check stop-loss (max 3% risk)
        stop_loss = risk_mgmt['stop_loss']
        max_stop_distance = current_price * 0.03
        if abs(entry_price - stop_loss) > max_stop_distance:
            if analysis.get('recommended_action') == 'long':
                risk_mgmt['stop_loss'] = entry_price - max_stop_distance
            else:
                risk_mgmt['stop_loss'] = entry_price + max_stop_distance
        
        # Validate take profits (minimum 1:2 risk/reward)
        risk = abs(entry_price - risk_mgmt['stop_loss'])
        min_reward = risk * 2
        
        if analysis.get('recommended_action') == 'long':
            min_tp1 = entry_price + min_reward
            if risk_mgmt.get('take_profit_1', 0) < min_tp1:
                risk_mgmt['take_profit_1'] = min_tp1
                risk_mgmt['take_profit_2'] = min_tp1 * 1.5
        else:
            min_tp1 = entry_price - min_reward
            if risk_mgmt.get('take_profit_1', 0) > min_tp1:
                risk_mgmt['take_profit_1'] = min_tp1
                risk_mgmt['take_profit_2'] = min_tp1 / 1.5
        
        # Calculate risk/reward ratio
        reward = abs(risk_mgmt.get('take_profit_1', entry_price) - entry_price)
        risk_mgmt['risk_reward_ratio'] = reward / risk if risk > 0 else 2.0
        
        # Add metadata
        analysis['timestamp'] = datetime.now().isoformat()
        analysis['analyzer'] = 'claude_enhanced'
        analysis['symbol'] = market_data.get('symbol', 'UNKNOWN')
        
        return analysis
    
    def get_enhanced_default_value(self, field: str, current_price: float):
        """Get enhanced default values for missing fields"""
        defaults = {
            'market_sentiment': 'neutral',
            'confidence_score': 0.3,
            'recommended_action': 'wait',
            'entry_strategy': {
                'entry_price': current_price,
                'entry_condition': 'market order',
                'position_size_percent': 2
            },
            'risk_management': {
                'stop_loss': current_price * 0.98,
                'take_profit_1': current_price * 1.04,
                'take_profit_2': current_price * 1.08,
                'risk_reward_ratio': 2.0,
                'max_loss_percent': 2.0
            },
            'reasoning': 'Analysis performed with default parameters due to incomplete data'
        }
        return defaults.get(field, {})
