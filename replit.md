# Intelligent Trading AI System

## Overview
A comprehensive intelligent trading AI system focused on Forex and commodity markets (EURUSD, XAUUSD, GBPUSD, etc.) with advanced ICT/SMC/SND methodologies, real-time market analysis, signal grading, interactive charts, and backtesting capabilities.

## Features
- **Real-time Market Analysis**: Live price data, technical indicators, and market structure analysis
- **Signal Grading System (E→S)**: Comprehensive confluence-based signal grading from E (weak) to S (strongest)
- **ICT/SMC Pattern Detection**: Order blocks, fair value gaps, liquidity sweeps, breaker blocks
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ADX, ATR, Stochastic, OBV, VWAP, CCI, Williams %R
- **Candlestick Patterns**: Hammer, engulfing, morning/evening star, three soldiers/crows, doji, harami
- **Live Narration**: Real-time commentary explaining market conditions and predictions
- **Backtesting Engine**: Historical strategy testing with performance metrics
- **Interactive Charts**: Beautiful, responsive chart interface with real-time updates
- **WebSocket Integration**: Real-time data streaming via Socket.IO

## Project Structure
```
├── app.py                    # Flask application with REST API and WebSocket
├── models.py                 # SQLAlchemy database models
├── trading_engine.py         # Core trading analysis engine
├── technical_indicators.py   # 100+ technical indicator calculations
├── pattern_detector.py       # Candlestick and chart pattern detection
├── smc_analyzer.py           # Smart Money Concepts analysis
├── market_data.py            # Market data fetching and simulation
├── backtester.py             # Strategy backtesting engine
├── templates/
│   └── index.html            # Main application template
└── static/
    ├── css/style.css         # Application styling
    └── js/app.js             # Frontend JavaScript
```

## Architecture

### Backend (Python/Flask)
- **Flask**: Web framework with REST API
- **Flask-SocketIO**: Real-time WebSocket communication
- **Flask-SQLAlchemy**: Database ORM with PostgreSQL
- **Flask-CORS**: Cross-origin resource sharing

### Trading Engine Components
1. **TradingEngine**: Main analysis orchestrator
2. **TechnicalIndicators**: RSI, MACD, Bollinger, ADX, ATR, etc.
3. **PatternDetector**: Candlestick and chart pattern recognition
4. **SMCAnalyzer**: ICT/SMC concepts (order blocks, FVGs, liquidity)
5. **MarketDataFetcher**: Historical and real-time data
6. **Backtester**: Strategy backtesting with performance metrics

### Frontend (HTML/CSS/JavaScript)
- Modern dark theme UI
- Chart.js for price visualization
- Socket.IO client for real-time updates
- Responsive design with grid layout

## API Endpoints
- `GET /` - Main application page
- `GET /api/market-data/<symbol>` - Historical OHLCV data
- `GET /api/analysis/<symbol>` - Complete market analysis
- `GET /api/signals` - Recent trading signals
- `GET /api/trades` - Trade history
- `POST /api/backtest` - Run strategy backtest
- `GET /api/backtest-results` - Historical backtest results
- `GET /api/supported-pairs` - Available trading pairs
- `GET /api/strategies` - Available trading strategies

## WebSocket Events
- `connect` - Client connection
- `subscribe` - Subscribe to symbol updates
- `request_analysis` - Request market analysis
- `request_live_narration` - Request live market commentary

## Signal Grading System
| Grade | Score | Description |
|-------|-------|-------------|
| S | 80+ | Exceptional setup with 6+ confluence factors |
| A | 65+ | Strong setup with 5+ confluence factors |
| B | 50+ | Good setup with 4+ confluence factors |
| C | 35+ | Moderate setup with 3+ confluence factors |
| D | 20+ | Weak setup, monitor only |
| E | <20 | No clear setup |

## Supported Markets
- Forex: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CHF, USD/CAD, NZD/USD, EUR/GBP, EUR/JPY, GBP/JPY
- Commodities: XAU/USD (Gold), XAG/USD (Silver)
- Crypto: BTC/USD, ETH/USD

## Development
- **Port**: 5000 (Frontend/API)
- **Database**: PostgreSQL (via DATABASE_URL)
- **Python Version**: 3.11

## Recent Changes
- Initial system implementation with full trading AI capabilities
- Implemented ICT/SMC pattern detection and analysis
- Built comprehensive signal grading system
- Created interactive web interface with real-time updates
- Added backtesting engine with performance metrics
