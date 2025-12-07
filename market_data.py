import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import math

class MarketDataFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60
        
        self.base_prices = {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
            'USD/JPY': 149.50,
            'AUD/USD': 0.6550,
            'USD/CHF': 0.8850,
            'USD/CAD': 1.3550,
            'NZD/USD': 0.6150,
            'EUR/GBP': 0.8580,
            'EUR/JPY': 162.20,
            'GBP/JPY': 189.10,
            'XAU/USD': 2035.50,
            'XAG/USD': 23.45,
            'BTC/USD': 43500.00,
            'ETH/USD': 2350.00,
        }
        
        self.volatility = {
            'EUR/USD': 0.0005,
            'GBP/USD': 0.0007,
            'USD/JPY': 0.05,
            'AUD/USD': 0.0006,
            'USD/CHF': 0.0005,
            'USD/CAD': 0.0005,
            'NZD/USD': 0.0006,
            'EUR/GBP': 0.0004,
            'EUR/JPY': 0.08,
            'GBP/JPY': 0.10,
            'XAU/USD': 5.0,
            'XAG/USD': 0.15,
            'BTC/USD': 500.0,
            'ETH/USD': 30.0,
        }
    
    def get_historical_data(self, symbol, timeframe='1h', limit=100):
        cache_key = f"{symbol}_{timeframe}_{limit}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.utcnow() - timestamp).seconds < self.cache_duration:
                return cached_data
        
        data = self._generate_realistic_data(symbol, timeframe, limit)
        self.cache[cache_key] = (data, datetime.utcnow())
        
        return data
    
    def _generate_realistic_data(self, symbol, timeframe, limit):
        base_price = self.base_prices.get(symbol, 1.0)
        vol = self.volatility.get(symbol, 0.001)
        
        timeframe_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440,
            '1w': 10080
        }
        
        minutes = timeframe_minutes.get(timeframe, 60)
        
        data = []
        current_time = datetime.utcnow()
        price = base_price
        
        trend = random.choice([-1, 0, 1])
        trend_strength = random.uniform(0.0001, 0.0003)
        
        for i in range(limit, 0, -1):
            timestamp = current_time - timedelta(minutes=i * minutes)
            
            trend_component = trend * trend_strength * (limit - i)
            
            cycle_component = 0.002 * base_price * math.sin(2 * math.pi * i / 24)
            
            noise = random.gauss(0, vol)
            
            price = base_price + trend_component + cycle_component + noise
            
            high_factor = abs(random.gauss(0, vol * 0.5))
            low_factor = abs(random.gauss(0, vol * 0.5))
            
            open_price = price + random.gauss(0, vol * 0.2)
            close_price = price + random.gauss(0, vol * 0.2)
            high_price = max(open_price, close_price) + high_factor
            low_price = min(open_price, close_price) - low_factor
            
            volume = random.uniform(1000, 10000) * (1 + 0.5 * math.sin(2 * math.pi * timestamp.hour / 24))
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5),
                'volume': round(volume, 2)
            })
        
        self._add_market_patterns(data, symbol)
        
        return data
    
    def _add_market_patterns(self, data, symbol):
        if len(data) < 20:
            return
        
        if random.random() > 0.7:
            idx = random.randint(10, len(data) - 5)
            for i in range(3):
                if idx + i < len(data):
                    data[idx + i]['close'] = data[idx + i]['open'] * (1 + random.uniform(0.001, 0.003))
                    data[idx + i]['high'] = max(data[idx + i]['high'], data[idx + i]['close'] * 1.001)
        
        if random.random() > 0.8:
            idx = random.randint(5, len(data) - 3)
            if idx + 2 < len(data):
                base = data[idx]['close']
                data[idx + 1]['low'] = base * 0.998
                data[idx + 1]['high'] = base * 1.003
                data[idx + 1]['close'] = data[idx + 1]['high']
        
        if random.random() > 0.7:
            idx = random.randint(15, len(data) - 2)
            vol = self.volatility.get(symbol, 0.001)
            data[idx]['high'] = data[idx]['close'] * (1 + vol * 3)
            data[idx]['close'] = data[idx]['open']
    
    def get_current_price(self, symbol):
        data = self.get_historical_data(symbol, '1m', 1)
        if data:
            return data[-1]['close']
        return self.base_prices.get(symbol, 1.0)
    
    def get_multiple_timeframes(self, symbol, timeframes=['1m', '5m', '15m', '1h', '4h']):
        result = {}
        for tf in timeframes:
            result[tf] = self.get_historical_data(symbol, tf, 100)
        return result


class LiveMarketSimulator:
    def __init__(self):
        self.fetcher = MarketDataFetcher()
        self.subscribers = {}
    
    def simulate_tick(self, symbol):
        current_data = self.fetcher.get_historical_data(symbol, '1m', 1)
        if current_data:
            base = current_data[-1]['close']
            vol = self.fetcher.volatility.get(symbol, 0.001)
            
            tick = {
                'symbol': symbol,
                'bid': round(base - vol * 0.1, 5),
                'ask': round(base + vol * 0.1, 5),
                'mid': round(base, 5),
                'spread': round(vol * 0.2, 6),
                'timestamp': datetime.utcnow().isoformat()
            }
            return tick
        return None
    
    def get_order_book(self, symbol, depth=10):
        current_price = self.fetcher.get_current_price(symbol)
        vol = self.fetcher.volatility.get(symbol, 0.001)
        
        bids = []
        asks = []
        
        for i in range(depth):
            bid_price = current_price - (i + 1) * vol * 0.1
            ask_price = current_price + (i + 1) * vol * 0.1
            
            bid_size = random.uniform(100, 1000) * (depth - i) / depth
            ask_size = random.uniform(100, 1000) * (depth - i) / depth
            
            bids.append({'price': round(bid_price, 5), 'size': round(bid_size, 2)})
            asks.append({'price': round(ask_price, 5), 'size': round(ask_size, 2)})
        
        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': datetime.utcnow().isoformat()
        }
