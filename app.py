import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Load configuration
try:
    from config import Config
    app.config.from_object(Config)
except ImportError:
    # Fallback to default SQLite configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trading-ai-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

CORS(app)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

from models import Trade, Signal, BacktestResult, MarketData, UserSettings
from trading_engine import TradingEngine
from market_data import MarketDataFetcher
from backtester import Backtester

trading_engine = TradingEngine()
market_fetcher = MarketDataFetcher()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    symbol = symbol.replace('-', '/')
    timeframe = request.args.get('timeframe', '1h')
    limit = int(request.args.get('limit', 100))
    data = market_fetcher.get_historical_data(symbol, timeframe, limit)
    return jsonify(data)

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    symbol = symbol.replace('-', '/')
    timeframe = request.args.get('timeframe', '1h')
    data = market_fetcher.get_historical_data(symbol, timeframe, 200)
    analysis = trading_engine.analyze_market(symbol, data)
    return jsonify(analysis)

@app.route('/api/signals')
def get_signals():
    with app.app_context():
        signals = Signal.query.order_by(Signal.timestamp.desc()).limit(50).all()
        return jsonify([s.to_dict() for s in signals])

@app.route('/api/trades')
def get_trades():
    with app.app_context():
        trades = Trade.query.order_by(Trade.entry_time.desc()).limit(50).all()
        return jsonify([t.to_dict() for t in trades])

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    data = request.get_json()
    symbol = data.get('symbol', 'EUR/USD')
    strategy = data.get('strategy', 'smc_ict')
    initial_capital = data.get('initial_capital', 10000)
    
    backtester = Backtester(initial_capital=initial_capital)
    result = backtester.run_backtest(symbol, strategy)
    
    try:
        with app.app_context():
            backtest = BacktestResult(
                symbol=symbol,
                strategy=strategy,
                initial_capital=float(initial_capital),
                final_capital=float(result['final_capital']),
                total_trades=int(result['total_trades']),
                win_rate=float(result['win_rate']),
                sharpe_ratio=float(result['sharpe_ratio']),
                max_drawdown=float(result['max_drawdown']),
                total_pips=float(result['total_pips']),
                result_data=json.dumps(result, default=str)
            )
            db.session.add(backtest)
            db.session.commit()
    except Exception as e:
        print(f"Error saving backtest result: {e}")
    
    return jsonify(result)

@app.route('/api/backtest-results')
def get_backtest_results():
    with app.app_context():
        results = BacktestResult.query.order_by(BacktestResult.timestamp.desc()).limit(10).all()
        return jsonify([r.to_dict() for r in results])

@app.route('/api/supported-pairs')
def get_supported_pairs():
    pairs = [
        {'symbol': 'EUR/USD', 'name': 'Euro/US Dollar', 'category': 'forex'},
        {'symbol': 'GBP/USD', 'name': 'British Pound/US Dollar', 'category': 'forex'},
        {'symbol': 'USD/JPY', 'name': 'US Dollar/Japanese Yen', 'category': 'forex'},
        {'symbol': 'AUD/USD', 'name': 'Australian Dollar/US Dollar', 'category': 'forex'},
        {'symbol': 'USD/CHF', 'name': 'US Dollar/Swiss Franc', 'category': 'forex'},
        {'symbol': 'USD/CAD', 'name': 'US Dollar/Canadian Dollar', 'category': 'forex'},
        {'symbol': 'NZD/USD', 'name': 'New Zealand Dollar/US Dollar', 'category': 'forex'},
        {'symbol': 'EUR/GBP', 'name': 'Euro/British Pound', 'category': 'forex'},
        {'symbol': 'EUR/JPY', 'name': 'Euro/Japanese Yen', 'category': 'forex'},
        {'symbol': 'GBP/JPY', 'name': 'British Pound/Japanese Yen', 'category': 'forex'},
        {'symbol': 'XAU/USD', 'name': 'Gold/US Dollar', 'category': 'commodity'},
        {'symbol': 'XAG/USD', 'name': 'Silver/US Dollar', 'category': 'commodity'},
        {'symbol': 'BTC/USD', 'name': 'Bitcoin/US Dollar', 'category': 'crypto'},
        {'symbol': 'ETH/USD', 'name': 'Ethereum/US Dollar', 'category': 'crypto'},
    ]
    return jsonify(pairs)

@app.route('/api/strategies')
def get_strategies():
    strategies = [
        {'id': 'smc_ict', 'name': 'SMC/ICT Strategy', 'description': 'Smart Money Concepts with ICT methodology'},
        {'id': 'liquidity_grab', 'name': 'Liquidity Grab', 'description': 'Asian session liquidity sweep strategy'},
        {'id': 'order_block', 'name': 'Order Block Trading', 'description': 'Trade based on institutional order blocks'},
        {'id': 'fvg_strategy', 'name': 'Fair Value Gap', 'description': 'Trade imbalances and fair value gaps'},
        {'id': 'breakout_retest', 'name': 'Breakout & Retest', 'description': 'Classic breakout with confirmation'},
        {'id': 'mean_reversion', 'name': 'Mean Reversion', 'description': 'Statistical mean reversion strategy'},
        {'id': 'momentum', 'name': 'Momentum Strategy', 'description': 'Trend following with momentum indicators'},
        {'id': 'multi_timeframe', 'name': 'Multi-Timeframe', 'description': 'Confluence across multiple timeframes'},
    ]
    return jsonify(strategies)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'Connected to Trading AI'})

@socketio.on('subscribe')
def handle_subscribe(data):
    symbol = data.get('symbol', 'EUR/USD')
    emit('subscribed', {'symbol': symbol, 'status': 'Subscribed'})

@socketio.on('request_analysis')
def handle_analysis_request(data):
    symbol = data.get('symbol', 'EUR/USD')
    timeframe = data.get('timeframe', '1h')
    
    market_data = market_fetcher.get_historical_data(symbol, timeframe, 200)
    analysis = trading_engine.analyze_market(symbol, market_data)
    
    emit('analysis_update', {
        'symbol': symbol,
        'analysis': analysis,
        'timestamp': datetime.utcnow().isoformat()
    })

@socketio.on('request_live_narration')
def handle_live_narration(data):
    symbol = data.get('symbol', 'EUR/USD')
    timeframe = data.get('timeframe', '15m')
    
    market_data = market_fetcher.get_historical_data(symbol, timeframe, 50)
    narration = trading_engine.generate_live_narration(symbol, market_data)
    
    emit('live_narration', {
        'symbol': symbol,
        'narration': narration,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"Starting Trading AI Server")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Server: http://localhost:{port}")
    print(f"{'='*60}\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
