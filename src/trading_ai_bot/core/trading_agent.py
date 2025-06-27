import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from ..tools.market_data import MarketDataTool
from .claude_analyzer import ClaudeMarketAnalyzer
from .risk_manager import RiskManager
from ..config import get_config, get_config_value

class TradingAgent:
    """
    Торговый агент для среднесрочной торговли на фьючерсах
    """
    
    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            config = get_config()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.position = None
        self.balance = get_config_value('trading.initial_balance', 10000)
        self.max_risk_per_trade = get_config_value('trading.max_risk_per_trade', 0.02)  # 2% риска на сделку
        self.data_provider = MarketDataTool(get_config_value('exchange', {}))
        self.claude_analyzer = ClaudeMarketAnalyzer(get_config_value('ai', {}))
        self.risk_manager = RiskManager(config.get('trading', {}))
        
    async def start(self):
        """Запуск торгового агента"""
        self.logger.info("Запуск торгового агента...")
        
        async with self.data_provider:
            while True:
                try:
                    # Получаем данные рынка
                    market_data = await self.get_market_data()
                    
                    # Анализируем с помощью AI
                    analysis = await self.analyze_market(market_data)
                    
                    # Принимаем торговое решение
                    decision = await self.make_trading_decision(analysis, market_data)
                    
                    # Исполняем решение
                    if decision:
                        await self.execute_trade(decision)
                    
                    # Ждем перед следующим циклом (например, 15 минут)
                    await asyncio.sleep(900)  
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в основном цикле: {e}")
                    await asyncio.sleep(60)  # Ждем минуту при ошибке
    
    async def get_market_data(self) -> Dict:
        """Получение данных рынка"""
        self.logger.info("Получение данных рынка...")
        
        # Получаем данные для первой торговой пары из конфигурации
        trading_pairs = self.config.get('trading_pairs', ['BTCUSDT'])
        symbol = trading_pairs[0]
        
        try:
            market_data = await self.data_provider.get_market_data(symbol)
            if market_data:
                self.logger.info(f"Данные получены для {symbol}: цена ${market_data['current_price']}, "
                               f"изменение за 24ч: {market_data['24h_change_percent']:.2f}%")
                return market_data
            else:
                self.logger.error(f"Не удалось получить данные для {symbol}")
                # Возвращаем заглушку в случае ошибки
                return {
                    "symbol": symbol,
                    "current_price": 50000.0,
                    "timestamp": datetime.now().isoformat(),
                    "error": "Fallback data"
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения данных: {e}")
            # Возвращаем заглушку в случае ошибки
            return {
                "symbol": symbol,
                "current_price": 50000.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def analyze_market(self, market_data: Dict) -> Dict:
        """Анализ рынка с помощью Claude"""
        self.logger.info("Анализ рынка с помощью AI...")
        
        try:
            # Используем Claude анализатор
            analysis = await self.claude_analyzer.analyze_market(market_data)
            
            # Дополнительная валидация результатов
            confidence = analysis.get('confidence_score', 0)
            sentiment = analysis.get('market_sentiment', 'neutral')
            
            if confidence > 0:
                self.logger.info(f"Анализ завершен: {sentiment} настроение, "
                               f"уверенность {confidence:.2f}, "
                               f"действие: {analysis.get('recommended_action', 'wait')}")
            else:
                self.logger.warning("Получен анализ с нулевой уверенностью")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа через Claude: {e}")
            # Возвращаем простой fallback анализ
            current_price = market_data.get("current_price", 50000)
            return {
                "market_sentiment": "neutral",
                "confidence_score": 0.3,
                "recommended_action": "wait",
                "entry_strategy": {
                    "entry_price": current_price,
                    "entry_condition": "fallback analysis",
                    "position_size_percent": 1
                },
                "risk_management": {
                    "stop_loss": current_price * 0.985,
                    "take_profit_1": current_price * 1.03,
                    "take_profit_2": current_price * 1.05,
                    "risk_reward_ratio": 2.0,
                    "max_loss_percent": 2.0
                },
                "reasoning": f"Fallback анализ из-за ошибки: {str(e)}",
                "analyzer": "fallback",
                "symbol": market_data.get('symbol', 'UNKNOWN')
            }
    
    async def make_trading_decision(self, analysis: Dict, market_data: Dict) -> Optional[Dict]:
        """Принятие торгового решения с учетом управления рисками"""
        reasoning = analysis.get('reasoning', '')
        self.logger.info(f"Анализ завершен: {reasoning[:100]}...")
        
        # Проверяем уровень уверенности (первичная проверка)
        confidence = analysis.get("confidence_score", 0)
        if confidence < 0.5:
            self.logger.info(f"Низкий уровень уверенности ({confidence:.2f}), пропускаем сделку")
            return None
        
        # Получаем рекомендованное действие
        recommended_action = analysis.get("recommended_action", "wait")
        if recommended_action == "wait":
            self.logger.info("Рекомендация: ждать, сделка не выполняется")
            return None
        
        # Создаем адаптированный анализ для риск-менеджера
        risk_analysis = self._adapt_analysis_for_risk_manager(analysis)
        
        # Используем риск-менеджер для расчета размера позиции
        position_calc = self.risk_manager.calculate_position_size(risk_analysis, market_data)
        
        if not position_calc['allowed']:
            self.logger.info(f"Сделка отклонена риск-менеджером: {position_calc['reason']}")
            return None
        
        # Получаем данные из анализа
        entry_strategy = analysis.get('entry_strategy', {})
        risk_management = analysis.get('risk_management', {})
        
        # Получаем символ из рыночных данных
        symbol = market_data.get('symbol', 'BTCUSDT')
        
        # Определяем действие на основе рекомендации
        action = "buy" if recommended_action == "long" else "sell"
        
        decision = {
            "action": action,
            "symbol": symbol,
            "size": position_calc['position_size'],
            "entry_price": entry_strategy.get('entry_price', market_data.get('current_price', 50000)),
            "stop_loss": risk_management.get('stop_loss', market_data.get('current_price', 50000) * 0.985),
            "take_profit": risk_management.get('take_profit_1', market_data.get('current_price', 50000) * 1.03),
            "confidence": confidence,
            "risk_amount": position_calc['risk_amount'],
            "potential_profit": position_calc['potential_profit'],
            "risk_reward_ratio": position_calc['risk_reward_ratio'],
            "kelly_fraction": position_calc.get('kelly_fraction', 0),
            "volatility_adjusted": position_calc.get('volatility_adjusted', 1.0),
            "analyzer_type": analysis.get('analyzer', 'unknown')
        }
        
        self.logger.info(f"Принято решение: {decision['action'].upper()} {decision['size']:.4f} {symbol} "
                        f"(риск: ${decision['risk_amount']:.2f}, R/R: {decision['risk_reward_ratio']:.2f})")
        
        return decision
    
    def _adapt_analysis_for_risk_manager(self, analysis: Dict) -> Dict:
        """Адаптирует новую структуру анализа под старый риск-менеджер"""
        entry_strategy = analysis.get('entry_strategy', {})
        risk_management = analysis.get('risk_management', {})
        
        # Переводим в старый формат для совместимости
        sentiment = analysis.get('market_sentiment', 'neutral')
        trend = 'bullish' if sentiment == 'bullish' else 'bearish' if sentiment == 'bearish' else 'sideways'
        
        return {
            'trend': trend,
            'confidence': analysis.get('confidence_score', 0),
            'entry_price': entry_strategy.get('entry_price', 50000),
            'stop_loss': risk_management.get('stop_loss', 49000),
            'take_profit': risk_management.get('take_profit_1', 51000),
            'risk_reward_ratio': risk_management.get('risk_reward_ratio', 2.0),
            'reasoning': analysis.get('reasoning', 'No reasoning provided')
        }
    
    async def execute_trade(self, decision: Dict):
        """Исполнение торгового решения"""
        self.logger.info(f"Исполнение сделки: {decision['symbol']} {decision['action']}")
        
        # Добавляем позицию в риск-менеджер
        position_added = self.risk_manager.add_position(decision)
        
        if position_added:
            # Для тестирования просто логируем
            analyzer_type = decision.get('analyzer_type', 'unknown')
            analyzer_emoji = "[DEBUG]" if analyzer_type in ['enhanced_mock', 'fallback'] else "[AI]"
            
            self.logger.info(f"ТОРГОВЫЙ СИГНАЛ {analyzer_emoji}: {decision['action'].upper()} "
                           f"{decision['size']:.4f} {decision['symbol']} по цене ${decision['entry_price']:.2f}")
            self.logger.info(f"   Риск: ${decision['risk_amount']:.2f} | "
                           f"Потенциал: ${decision['potential_profit']:.2f} | "
                           f"R/R: {decision['risk_reward_ratio']:.2f}")
            self.logger.info(f"   Уверенность: {decision['confidence']:.2%} | "
                           f"Kelly: {decision.get('kelly_fraction', 0):.2f}")
            self.logger.info(f"   Анализатор: {analyzer_type}")
            
            # Показываем сводку портфеля
            portfolio = self.risk_manager.get_portfolio_summary()
            self.logger.info(f"   Портфель: Позиций={portfolio['open_positions']}, "
                           f"Риск={portfolio['risk_percentage']:.1f}%, "
                           f"Сделок сегодня={portfolio['daily_trades']}")
        else:
            self.logger.error("Не удалось добавить позицию в риск-менеджер")
        
        # TODO: Здесь будет интеграция с торговым API
