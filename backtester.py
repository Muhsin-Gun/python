import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from market_data import MarketDataFetcher
from trading_engine import TradingEngine
import json

class Backtester:
    def __init__(self, initial_capital=10000, risk_per_trade=0.02):
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.market_fetcher = MarketDataFetcher()
        self.trading_engine = TradingEngine()
    
    def run_backtest(self, symbol, strategy, periods=200):
        data = self.market_fetcher.get_historical_data(symbol, '1h', periods)
        
        if not data or len(data) < 100:
            return self._empty_result(symbol, strategy)
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        capital = self.initial_capital
        trades = []
        equity_curve = [capital]
        positions = []
        
        lookback = 50
        
        for i in range(lookback, len(df) - 10):
            window = df.iloc[i-lookback:i+1]
            
            analysis = self.trading_engine.analyze_market(symbol, window.to_dict('records'))
            
            if analysis['signals']:
                signal = analysis['signals'][0]
                
                if signal['grade'] in ['S', 'A', 'B']:
                    current_price = float(df['close'].iloc[i])
                    atr = analysis['technical'].get('atr', {}).get('value', current_price * 0.001)
                    
                    if signal['direction'] == 'long':
                        stop_loss = current_price - (2 * atr)
                        take_profit = current_price + (3 * atr)
                    else:
                        stop_loss = current_price + (2 * atr)
                        take_profit = current_price - (3 * atr)
                    
                    risk_amount = capital * self.risk_per_trade
                    sl_distance = abs(current_price - stop_loss)
                    position_size = risk_amount / sl_distance if sl_distance > 0 else 0.01
                    
                    trade = {
                        'entry_index': i,
                        'entry_price': current_price,
                        'entry_time': str(df['timestamp'].iloc[i]),
                        'direction': signal['direction'],
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'position_size': position_size,
                        'grade': signal['grade'],
                        'status': 'open'
                    }
                    positions.append(trade)
            
            closed_positions = []
            for pos in positions:
                if pos['status'] == 'open':
                    current_high = float(df['high'].iloc[i])
                    current_low = float(df['low'].iloc[i])
                    current_close = float(df['close'].iloc[i])
                    
                    if pos['direction'] == 'long':
                        if current_low <= pos['stop_loss']:
                            pnl = (pos['stop_loss'] - pos['entry_price']) * pos['position_size']
                            pos['exit_price'] = pos['stop_loss']
                            pos['exit_reason'] = 'stop_loss'
                            pos['pnl'] = pnl
                            pos['pips'] = (pos['stop_loss'] - pos['entry_price']) * 10000
                            pos['status'] = 'closed'
                            pos['exit_time'] = str(df['timestamp'].iloc[i])
                            pos['exit_index'] = i
                            capital += pnl
                        elif current_high >= pos['take_profit']:
                            pnl = (pos['take_profit'] - pos['entry_price']) * pos['position_size']
                            pos['exit_price'] = pos['take_profit']
                            pos['exit_reason'] = 'take_profit'
                            pos['pnl'] = pnl
                            pos['pips'] = (pos['take_profit'] - pos['entry_price']) * 10000
                            pos['status'] = 'closed'
                            pos['exit_time'] = str(df['timestamp'].iloc[i])
                            pos['exit_index'] = i
                            capital += pnl
                    else:
                        if current_high >= pos['stop_loss']:
                            pnl = (pos['entry_price'] - pos['stop_loss']) * pos['position_size']
                            pos['exit_price'] = pos['stop_loss']
                            pos['exit_reason'] = 'stop_loss'
                            pos['pnl'] = pnl
                            pos['pips'] = (pos['entry_price'] - pos['stop_loss']) * 10000
                            pos['status'] = 'closed'
                            pos['exit_time'] = str(df['timestamp'].iloc[i])
                            pos['exit_index'] = i
                            capital += pnl
                        elif current_low <= pos['take_profit']:
                            pnl = (pos['entry_price'] - pos['take_profit']) * pos['position_size']
                            pos['exit_price'] = pos['take_profit']
                            pos['exit_reason'] = 'take_profit'
                            pos['pnl'] = pnl
                            pos['pips'] = (pos['entry_price'] - pos['take_profit']) * 10000
                            pos['status'] = 'closed'
                            pos['exit_time'] = str(df['timestamp'].iloc[i])
                            pos['exit_index'] = i
                            capital += pnl
                    
                    if pos['status'] == 'closed':
                        closed_positions.append(pos)
            
            for cp in closed_positions:
                trades.append(cp)
                positions.remove(cp)
            
            equity_curve.append(capital)
        
        for pos in positions:
            if pos['status'] == 'open':
                current_price = float(df['close'].iloc[-1])
                if pos['direction'] == 'long':
                    pnl = (current_price - pos['entry_price']) * pos['position_size']
                    pos['pips'] = (current_price - pos['entry_price']) * 10000
                else:
                    pnl = (pos['entry_price'] - current_price) * pos['position_size']
                    pos['pips'] = (pos['entry_price'] - current_price) * 10000
                pos['exit_price'] = current_price
                pos['exit_reason'] = 'end_of_backtest'
                pos['pnl'] = pnl
                pos['status'] = 'closed'
                pos['exit_time'] = str(df['timestamp'].iloc[-1])
                capital += pnl
                trades.append(pos)
        
        return self._calculate_metrics(symbol, strategy, trades, equity_curve)
    
    def _calculate_metrics(self, symbol, strategy, trades, equity_curve):
        if not trades:
            return self._empty_result(symbol, strategy)
        
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        
        total_pips = sum(t.get('pips', 0) for t in trades)
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losing_trades])) if losing_trades else 1
        profit_factor = abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades and sum(t['pnl'] for t in losing_trades) != 0 else 0
        
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        sharpe_ratio = 0
        if len(returns) > 1 and returns.std() != 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak
        max_drawdown = abs(drawdown.min()) * 100 if len(drawdown) > 0 else 0
        
        final_capital = equity_curve[-1] if equity_curve else self.initial_capital
        
        grade_distribution = {}
        for t in trades:
            grade = t.get('grade', 'Unknown')
            if grade not in grade_distribution:
                grade_distribution[grade] = {'count': 0, 'wins': 0, 'total_pnl': 0}
            grade_distribution[grade]['count'] += 1
            if t['pnl'] > 0:
                grade_distribution[grade]['wins'] += 1
            grade_distribution[grade]['total_pnl'] += t['pnl']
        
        for grade in grade_distribution:
            count = grade_distribution[grade]['count']
            grade_distribution[grade]['win_rate'] = (grade_distribution[grade]['wins'] / count * 100) if count > 0 else 0
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'initial_capital': self.initial_capital,
            'final_capital': round(final_capital, 2),
            'total_return': round((final_capital - self.initial_capital) / self.initial_capital * 100, 2),
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'total_pips': round(total_pips, 1),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'equity_curve': equity_curve[::10] if len(equity_curve) > 50 else equity_curve,
            'trades': trades[-20:],
            'grade_distribution': grade_distribution,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _empty_result(self, symbol, strategy):
        return {
            'symbol': symbol,
            'strategy': strategy,
            'initial_capital': self.initial_capital,
            'final_capital': self.initial_capital,
            'total_return': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pips': 0,
            'total_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'equity_curve': [self.initial_capital],
            'trades': [],
            'grade_distribution': {},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def run_multiple_backtests(self, symbol, strategy, iterations=5):
        results = []
        
        for i in range(iterations):
            result = self.run_backtest(symbol, strategy, periods=300 + i * 50)
            result['iteration'] = i + 1
            results.append(result)
        
        avg_win_rate = np.mean([r['win_rate'] for r in results])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
        avg_return = np.mean([r['total_return'] for r in results])
        avg_drawdown = np.mean([r['max_drawdown'] for r in results])
        total_trades = sum(r['total_trades'] for r in results)
        
        consistency_score = 100 - (np.std([r['total_return'] for r in results]) * 10)
        consistency_score = max(0, min(100, consistency_score))
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'iterations': iterations,
            'results': results,
            'summary': {
                'avg_win_rate': round(avg_win_rate, 2),
                'avg_sharpe_ratio': round(avg_sharpe, 2),
                'avg_return': round(avg_return, 2),
                'avg_max_drawdown': round(avg_drawdown, 2),
                'total_trades': total_trades,
                'consistency_score': round(consistency_score, 2)
            },
            'assessment': self._generate_assessment(avg_win_rate, avg_sharpe, avg_return, avg_drawdown, consistency_score),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_assessment(self, win_rate, sharpe, returns, drawdown, consistency):
        assessment = []
        
        if sharpe > 1.5:
            assessment.append("Excellent risk-adjusted returns (Sharpe > 1.5)")
        elif sharpe > 1.0:
            assessment.append("Good risk-adjusted returns (Sharpe > 1.0)")
        elif sharpe > 0.5:
            assessment.append("Acceptable risk-adjusted returns")
        else:
            assessment.append("Low risk-adjusted returns - strategy needs improvement")
        
        if win_rate > 60:
            assessment.append("Strong win rate above 60%")
        elif win_rate > 50:
            assessment.append("Adequate win rate above 50%")
        else:
            assessment.append("Win rate below 50% - consider tighter entry criteria")
        
        if drawdown < 10:
            assessment.append("Low maximum drawdown - good risk control")
        elif drawdown < 20:
            assessment.append("Moderate drawdown - acceptable risk level")
        else:
            assessment.append("High drawdown - implement stricter risk management")
        
        if consistency > 80:
            assessment.append("Highly consistent performance across iterations")
        elif consistency > 60:
            assessment.append("Reasonably consistent performance")
        else:
            assessment.append("Inconsistent performance - strategy may be curve-fitted")
        
        return assessment
