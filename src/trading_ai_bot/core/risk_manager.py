import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Position:
    """Класс для хранения информации о позиции"""
    symbol: str
    side: str  # 'long' или 'short'
    size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    confidence: float
    risk_amount: float
    expected_return: float

class RiskManager:
    """
    Модуль управления рисками и размерами позиций
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Параметры управления рисками
        self.balance = config.get('initial_balance', 10000)
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.02)  # 2%
        self.max_portfolio_risk = config.get('max_portfolio_risk', 0.06)  # 6%
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 5%
        self.min_risk_reward_ratio = config.get('min_risk_reward_ratio', 2.0)
        
        # Дополнительные параметры
        self.max_positions = config.get('max_positions', 3)
        self.correlation_limit = config.get('correlation_limit', 0.7)
        self.volatility_adjustment = config.get('volatility_adjustment', True)
        
        # Отслеживание состояния
        self.current_positions: List[Position] = []
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.max_daily_trades = config.get('max_daily_trades', 10)
        
        # История для Kelly Criterion
        self.trade_history: List[Dict] = []
        self.win_rate = 0.0
        self.avg_win = 0.0
        self.avg_loss = 0.0
        
        self.logger.info(f"RiskManager инициализирован с балансом ${self.balance:,.2f}")
    
    def calculate_position_size(self, analysis: Dict, market_data: Dict) -> Dict:
        """
        Расчет размера позиции с учетом рисков
        
        Args:
            analysis: Результат анализа от Claude
            market_data: Рыночные данные
            
        Returns:
            Dict с информацией о позиции и рисках
        """
        
        symbol = market_data.get('symbol', 'UNKNOWN')
        entry_price = analysis.get('entry_price', 0)
        stop_loss = analysis.get('stop_loss', 0)
        take_profit = analysis.get('take_profit', 0)
        confidence = analysis.get('confidence', 0)
        
        self.logger.info(f"Расчет размера позиции для {symbol}")
        
        # Проверка базовых условий
        risk_checks = self._perform_risk_checks(analysis, market_data)
        if not risk_checks['passed']:
            return {
                'position_size': 0,
                'risk_amount': 0,
                'reason': risk_checks['reason'],
                'allowed': False
            }
        
        # Расчет риска на единицу
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit <= 0:
            return {
                'position_size': 0,
                'risk_amount': 0,
                'reason': 'Невозможно определить риск на единицу',
                'allowed': False
            }
        
        # Базовый размер позиции (фиксированный процент)
        base_risk_amount = self.balance * self.max_risk_per_trade
        base_position_size = base_risk_amount / risk_per_unit
        
        # Корректировки размера позиции
        adjusted_size = self._adjust_position_size(
            base_position_size, 
            confidence, 
            analysis, 
            market_data
        )
        
        # Финальные проверки и ограничения
        final_size = self._apply_position_limits(adjusted_size, entry_price)
        final_risk_amount = final_size * risk_per_unit
        
        # Расчет ожидаемой прибыли
        potential_profit = abs(take_profit - entry_price) * final_size
        risk_reward_ratio = potential_profit / final_risk_amount if final_risk_amount > 0 else 0
        
        result = {
            'position_size': final_size,
            'risk_amount': final_risk_amount,
            'potential_profit': potential_profit,
            'risk_reward_ratio': risk_reward_ratio,
            'confidence_adjusted': confidence,
            'volatility_adjusted': self._calculate_volatility_factor(market_data),
            'kelly_fraction': self._calculate_kelly_fraction(analysis),
            'allowed': final_size > 0,
            'reason': 'Позиция рассчитана успешно' if final_size > 0 else 'Размер позиции слишком мал'
        }
        
        self.logger.info(f"Расчет завершен: размер={final_size:.4f}, риск=${final_risk_amount:.2f}, R/R={risk_reward_ratio:.2f}")
        
        return result
    
    def _perform_risk_checks(self, analysis: Dict, market_data: Dict) -> Dict:
        """Выполнение проверок рисков"""
        
        # Проверка 1: Минимальная уверенность
        confidence = analysis.get('confidence', 0)
        if confidence < 0.5:
            return {'passed': False, 'reason': f'Низкая уверенность анализа: {confidence:.2%}'}
        
        # Проверка 2: Risk/Reward соотношение
        rr_ratio = analysis.get('risk_reward_ratio', 0)
        if rr_ratio < self.min_risk_reward_ratio:
            return {'passed': False, 'reason': f'Низкое R/R соотношение: {rr_ratio:.2f}'}
        
        # Проверка 3: Максимальное количество позиций
        if len(self.current_positions) >= self.max_positions:
            return {'passed': False, 'reason': f'Достигнут лимит позиций: {self.max_positions}'}
        
        # Проверка 4: Дневной лимит убытков
        daily_loss_percent = abs(self.daily_pnl) / self.balance
        if self.daily_pnl < 0 and daily_loss_percent >= self.max_daily_loss:
            return {'passed': False, 'reason': f'Достигнут дневной лимит убытков: {daily_loss_percent:.2%}'}
        
        # Проверка 5: Лимит сделок в день
        if self.daily_trades >= self.max_daily_trades:
            return {'passed': False, 'reason': f'Достигнут лимит сделок в день: {self.max_daily_trades}'}
        
        # Проверка 6: Общий риск портфеля
        current_portfolio_risk = self._calculate_portfolio_risk()
        max_additional_risk = self.balance * self.max_portfolio_risk - current_portfolio_risk
        if max_additional_risk <= 0:
            return {'passed': False, 'reason': 'Достигнут лимит риска портфеля'}
        
        return {'passed': True, 'reason': 'Все проверки пройдены'}
    
    def _adjust_position_size(self, base_size: float, confidence: float, 
                            analysis: Dict, market_data: Dict) -> float:
        """Корректировка размера позиции по различным факторам"""
        
        adjusted_size = base_size
        
        # 1. Корректировка по уверенности (Kelly-подобный подход)
        confidence_multiplier = self._calculate_confidence_multiplier(confidence)
        adjusted_size *= confidence_multiplier
        
        # 2. Корректировка по волатильности
        if self.volatility_adjustment:
            volatility_factor = self._calculate_volatility_factor(market_data)
            adjusted_size *= volatility_factor
        
        # 3. Корректировка по времени удержания
        time_horizon = analysis.get('time_horizon', '2-4 часа')
        time_multiplier = self._calculate_time_multiplier(time_horizon)
        adjusted_size *= time_multiplier
        
        # 4. Корректировка по объему (ликвидности)
        volume_factor = self._calculate_volume_factor(market_data)
        adjusted_size *= volume_factor
        
        self.logger.debug(f"Корректировки: уверенность={confidence_multiplier:.2f}, "
                         f"волатильность={volatility_factor:.2f}, время={time_multiplier:.2f}, "
                         f"объем={volume_factor:.2f}")
        
        return adjusted_size
    
    def _calculate_confidence_multiplier(self, confidence: float) -> float:
        """Расчет мультипликатора по уверенности"""
        # Нелинейная функция: низкая уверенность сильно снижает размер
        if confidence < 0.6:
            return 0.5
        elif confidence < 0.7:
            return 0.7
        elif confidence < 0.8:
            return 0.9
        elif confidence < 0.9:
            return 1.0
        else:
            return 1.2  # Премия за высокую уверенность
    
    def _calculate_volatility_factor(self, market_data: Dict) -> float:
        """Расчет фактора волатильности"""
        try:
            # Используем 24h изменение как прокси волатильности
            change_24h = abs(market_data.get('24h_change_percent', 0))
            
            # Нормализуем: 2% изменение = нормальная волатильность
            if change_24h < 1:
                return 1.2  # Низкая волатильность - увеличиваем размер
            elif change_24h < 3:
                return 1.0  # Нормальная волатильность
            elif change_24h < 5:
                return 0.8  # Высокая волатильность - снижаем размер
            else:
                return 0.6  # Очень высокая волатильность
                
        except Exception:
            return 1.0
    
    def _calculate_time_multiplier(self, time_horizon: str) -> float:
        """Расчет мультипликатора по времени удержания"""
        try:
            if isinstance(time_horizon, str):
                # Извлекаем числа из строки
                if '1' in time_horizon:
                    return 0.8  # Короткий горизонт - меньший размер
                elif '2' in time_horizon or '3' in time_horizon:
                    return 1.0  # Средний горизонт - базовый размер
                elif '4' in time_horizon or '6' in time_horizon:
                    return 1.1  # Длинный горизонт - больший размер
            return 1.0
        except Exception:
            return 1.0
    
    def _calculate_volume_factor(self, market_data: Dict) -> float:
        """Расчет фактора ликвидности по объему"""
        try:
            volume_24h = market_data.get('24h_volume', 0)
            
            # Примерные пороги для криптовалют (в USD)
            if volume_24h > 2_000_000_000:  # > 2B
                return 1.0  # Высокая ликвидность
            elif volume_24h > 1_000_000_000:  # > 1B
                return 0.9
            elif volume_24h > 500_000_000:  # > 500M
                return 0.8
            else:
                return 0.7  # Низкая ликвидность - снижаем размер
                
        except Exception:
            return 1.0
    
    def _apply_position_limits(self, size: float, entry_price: float) -> float:
        """Применение финальных лимитов на размер позиции"""
        
        # Лимит 1: Минимальный размер позиции
        min_position_value = 100  # $100 минимум
        min_size = min_position_value / entry_price
        if size < min_size:
            return 0  # Слишком маленькая позиция
        
        # Лимит 2: Максимальный процент от баланса на одну позицию
        max_position_percent = 0.25  # 25% от баланса максимум
        max_position_value = self.balance * max_position_percent
        max_size = max_position_value / entry_price
        
        # Лимит 3: Учет текущего риска портфеля
        current_risk = self._calculate_portfolio_risk()
        available_risk = self.balance * self.max_portfolio_risk - current_risk
        max_risk_size = available_risk / abs(entry_price - self._get_average_stop_distance(entry_price)) if available_risk > 0 else 0
        
        # Применяем самый строгий лимит
        final_size = min(size, max_size, max_risk_size) if max_risk_size > 0 else min(size, max_size)
        
        return max(0, final_size)
    
    def _get_average_stop_distance(self, entry_price: float) -> float:
        """Получить среднее расстояние до стоп-лосса"""
        return entry_price * 0.02  # 2% по умолчанию
    
    def _calculate_portfolio_risk(self) -> float:
        """Расчет текущего риска портфеля"""
        total_risk = 0
        for position in self.current_positions:
            total_risk += position.risk_amount
        return total_risk
    
    def _calculate_kelly_fraction(self, analysis: Dict) -> float:
        """Расчет Kelly Criterion для оптимального размера позиции"""
        try:
            if len(self.trade_history) < 10:
                return 0.5  # Недостаточно данных, консервативный подход
            
            # Обновляем статистику
            self._update_trade_statistics()
            
            # Kelly формула: f = (bp - q) / b
            # где b = отношение выигрыша к проигрышу
            # p = вероятность выигрыша
            # q = вероятность проигрыша (1-p)
            
            if self.avg_loss == 0 or self.win_rate == 0:
                return 0.25
            
            b = self.avg_win / abs(self.avg_loss)
            p = self.win_rate
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # Ограничиваем Kelly fraction разумными пределами
            kelly_fraction = max(0.1, min(0.5, kelly_fraction))
            
            return kelly_fraction
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета Kelly fraction: {e}")
            return 0.25
    
    def _update_trade_statistics(self):
        """Обновление статистики сделок для Kelly Criterion"""
        if not self.trade_history:
            return
        
        wins = [trade['pnl'] for trade in self.trade_history if trade['pnl'] > 0]
        losses = [trade['pnl'] for trade in self.trade_history if trade['pnl'] < 0]
        
        self.win_rate = len(wins) / len(self.trade_history) if self.trade_history else 0
        self.avg_win = sum(wins) / len(wins) if wins else 0
        self.avg_loss = sum(losses) / len(losses) if losses else 0
    
    def add_position(self, position_info: Dict) -> bool:
        """Добавление новой позиции"""
        try:
            position = Position(
                symbol=position_info['symbol'],
                side='long' if position_info['action'] == 'buy' else 'short',
                size=position_info['size'],
                entry_price=position_info['entry_price'],
                stop_loss=position_info['stop_loss'],
                take_profit=position_info['take_profit'],
                timestamp=datetime.now(),
                confidence=position_info['confidence'],
                risk_amount=position_info.get('risk_amount', 0),
                expected_return=position_info.get('potential_profit', 0)
            )
            
            self.current_positions.append(position)
            self.daily_trades += 1
            
            self.logger.info(f"Добавлена позиция: {position.symbol} {position.side} "
                           f"размер={position.size:.4f} риск=${position.risk_amount:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления позиции: {e}")
            return False
    
    def close_position(self, symbol: str, close_price: float) -> Optional[Dict]:
        """Закрытие позиции"""
        for i, position in enumerate(self.current_positions):
            if position.symbol == symbol:
                # Расчет P&L
                if position.side == 'long':
                    pnl = (close_price - position.entry_price) * position.size
                else:
                    pnl = (position.entry_price - close_price) * position.size
                
                # Обновляем статистику
                self.daily_pnl += pnl
                
                # Добавляем в историю
                trade_record = {
                    'symbol': position.symbol,
                    'side': position.side,
                    'entry_price': position.entry_price,
                    'close_price': close_price,
                    'size': position.size,
                    'pnl': pnl,
                    'timestamp': datetime.now(),
                    'confidence': position.confidence
                }
                
                self.trade_history.append(trade_record)
                
                # Удаляем позицию
                self.current_positions.pop(i)
                
                self.logger.info(f"Закрыта позиция {symbol}: P&L=${pnl:.2f}")
                
                return trade_record
        
        return None
    
    def get_portfolio_summary(self) -> Dict:
        """Получение сводки по портфелю"""
        total_risk = self._calculate_portfolio_risk()
        
        return {
            'balance': self.balance,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'open_positions': len(self.current_positions),
            'total_risk': total_risk,
            'risk_percentage': (total_risk / self.balance * 100) if self.balance > 0 else 0,
            'available_risk': max(0, self.balance * self.max_portfolio_risk - total_risk),
            'win_rate': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'total_trades': len(self.trade_history)
        }
    
    def reset_daily_stats(self):
        """Сброс дневной статистики"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.logger.info("Дневная статистика сброшена")
