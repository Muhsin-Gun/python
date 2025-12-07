from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

def get_db():
    from app import db
    return db

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    position_size = db.Column(db.Float, default=0.01)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime)
    pnl = db.Column(db.Float, default=0.0)
    pips = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='open')
    signal_grade = db.Column(db.String(5))
    strategy = db.Column(db.String(50))
    reasoning = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'pnl': self.pnl,
            'pips': self.pips,
            'status': self.status,
            'signal_grade': self.signal_grade,
            'strategy': self.strategy,
            'reasoning': self.reasoning
        }

class Signal(db.Model):
    __tablename__ = 'signals'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    signal_type = db.Column(db.String(50), nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    confidence = db.Column(db.Float, default=0.0)
    entry_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    risk_reward = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime)
    reasoning = db.Column(db.Text)
    contributors = db.Column(db.Text)
    prediction = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    outcome = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'direction': self.direction,
            'grade': self.grade,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_reward': self.risk_reward,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'expiry': self.expiry.isoformat() if self.expiry else None,
            'reasoning': self.reasoning,
            'contributors': json.loads(self.contributors) if self.contributors else [],
            'prediction': json.loads(self.prediction) if self.prediction else {},
            'status': self.status,
            'outcome': self.outcome
        }

class BacktestResult(db.Model):
    __tablename__ = 'backtest_results'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    initial_capital = db.Column(db.Float, default=10000)
    final_capital = db.Column(db.Float)
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    sharpe_ratio = db.Column(db.Float, default=0.0)
    max_drawdown = db.Column(db.Float, default=0.0)
    total_pips = db.Column(db.Float, default=0.0)
    avg_trade_duration = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    result_data = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'strategy': self.strategy,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'total_pips': self.total_pips,
            'avg_trade_duration': self.avg_trade_duration,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'result_data': json.loads(self.result_data) if self.result_data else {}
        }

class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, default=0)
    
    __table_args__ = (
        db.Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    risk_per_trade = db.Column(db.Float, default=1.0)
    max_daily_loss = db.Column(db.Float, default=5.0)
    max_weekly_drawdown = db.Column(db.Float, default=10.0)
    preferred_pairs = db.Column(db.Text)
    trading_mode = db.Column(db.String(20), default='manual')
    analysis_mode = db.Column(db.String(20), default='trader')
    timezone = db.Column(db.String(50), default='UTC')
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'risk_per_trade': self.risk_per_trade,
            'max_daily_loss': self.max_daily_loss,
            'max_weekly_drawdown': self.max_weekly_drawdown,
            'preferred_pairs': json.loads(self.preferred_pairs) if self.preferred_pairs else [],
            'trading_mode': self.trading_mode,
            'analysis_mode': self.analysis_mode,
            'timezone': self.timezone,
            'notifications_enabled': self.notifications_enabled
        }
