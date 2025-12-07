import numpy as np
import pandas as pd
from datetime import datetime

class TechnicalIndicators:
    def calculate_all(self, df):
        if len(df) < 20:
            return {}
        
        results = {}
        
        results['rsi'] = self.calculate_rsi(df)
        results['macd'] = self.calculate_macd(df)
        results['bollinger'] = self.calculate_bollinger_bands(df)
        results['atr'] = self.calculate_atr(df)
        results['adx'] = self.calculate_adx(df)
        results['stochastic'] = self.calculate_stochastic(df)
        results['ema'] = self.calculate_ema_set(df)
        results['sma'] = self.calculate_sma_set(df)
        results['momentum'] = self.calculate_momentum(df)
        results['obv'] = self.calculate_obv(df)
        results['vwap'] = self.calculate_vwap(df)
        results['williams_r'] = self.calculate_williams_r(df)
        results['cci'] = self.calculate_cci(df)
        
        return results
    
    def calculate_rsi(self, df, period=14):
        if len(df) < period + 1:
            return {'value': 50, 'signal': 'neutral'}
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss.replace(0, np.inf)
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50
        
        if current_rsi > 70:
            signal = 'overbought'
        elif current_rsi < 30:
            signal = 'oversold'
        else:
            signal = 'neutral'
        
        prev_rsi = float(rsi.iloc[-2]) if len(rsi) > 1 and not np.isnan(rsi.iloc[-2]) else current_rsi
        divergence = self._detect_rsi_divergence(df, rsi)
        
        return {
            'value': round(current_rsi, 2),
            'prev_value': round(prev_rsi, 2),
            'signal': signal,
            'divergence': divergence
        }
    
    def _detect_rsi_divergence(self, df, rsi):
        if len(df) < 20:
            return None
        
        prices = df['close'].values[-20:]
        rsi_values = rsi.values[-20:]
        
        if prices[-1] > prices[-10] and rsi_values[-1] < rsi_values[-10]:
            return 'bearish_divergence'
        elif prices[-1] < prices[-10] and rsi_values[-1] > rsi_values[-10]:
            return 'bullish_divergence'
        
        return None
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        if len(df) < slow + signal:
            return {'value': 0, 'signal': 'neutral', 'histogram': 0}
        
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        current_macd = float(macd_line.iloc[-1])
        current_signal = float(signal_line.iloc[-1])
        current_hist = float(histogram.iloc[-1])
        prev_hist = float(histogram.iloc[-2]) if len(histogram) > 1 else 0
        
        if current_macd > current_signal and prev_hist < current_hist:
            macd_signal = 'bullish'
        elif current_macd < current_signal and prev_hist > current_hist:
            macd_signal = 'bearish'
        else:
            macd_signal = 'neutral'
        
        crossover = None
        if len(macd_line) > 1 and len(signal_line) > 1:
            prev_macd = float(macd_line.iloc[-2])
            prev_signal = float(signal_line.iloc[-2])
            if prev_macd < prev_signal and current_macd > current_signal:
                crossover = 'bullish_crossover'
            elif prev_macd > prev_signal and current_macd < current_signal:
                crossover = 'bearish_crossover'
        
        return {
            'value': round(current_macd, 6),
            'signal_line': round(current_signal, 6),
            'histogram': round(current_hist, 6),
            'signal': macd_signal,
            'crossover': crossover
        }
    
    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        if len(df) < period:
            current = float(df['close'].iloc[-1])
            return {'upper': current, 'middle': current, 'lower': current, 'signal': 'neutral', 'width': 0}
        
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        current_price = float(df['close'].iloc[-1])
        upper_val = float(upper.iloc[-1])
        middle_val = float(sma.iloc[-1])
        lower_val = float(lower.iloc[-1])
        
        bandwidth = (upper_val - lower_val) / middle_val * 100 if middle_val > 0 else 0
        
        if current_price > upper_val:
            signal = 'overbought'
        elif current_price < lower_val:
            signal = 'oversold'
        else:
            signal = 'neutral'
        
        percent_b = (current_price - lower_val) / (upper_val - lower_val) * 100 if (upper_val - lower_val) > 0 else 50
        
        return {
            'upper': round(upper_val, 5),
            'middle': round(middle_val, 5),
            'lower': round(lower_val, 5),
            'width': round(bandwidth, 2),
            'percent_b': round(percent_b, 2),
            'signal': signal
        }
    
    def calculate_atr(self, df, period=14):
        if len(df) < period + 1:
            return {'value': 0, 'percent': 0}
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        current_atr = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else 0
        current_price = float(close.iloc[-1])
        atr_percent = (current_atr / current_price * 100) if current_price > 0 else 0
        
        return {
            'value': round(current_atr, 6),
            'percent': round(atr_percent, 4)
        }
    
    def calculate_adx(self, df, period=14):
        if len(df) < period * 2:
            return {'value': 25, 'plus_di': 25, 'minus_di': 25, 'trend_strength': 'weak'}
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff().abs()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.inf)
        adx = dx.rolling(window=period).mean()
        
        current_adx = float(adx.iloc[-1]) if not np.isnan(adx.iloc[-1]) else 25
        current_plus_di = float(plus_di.iloc[-1]) if not np.isnan(plus_di.iloc[-1]) else 25
        current_minus_di = float(minus_di.iloc[-1]) if not np.isnan(minus_di.iloc[-1]) else 25
        
        if current_adx > 50:
            trend_strength = 'very_strong'
        elif current_adx > 25:
            trend_strength = 'strong'
        elif current_adx > 20:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        return {
            'value': round(current_adx, 2),
            'plus_di': round(current_plus_di, 2),
            'minus_di': round(current_minus_di, 2),
            'trend_strength': trend_strength
        }
    
    def calculate_stochastic(self, df, k_period=14, d_period=3):
        if len(df) < k_period:
            return {'k': 50, 'd': 50, 'signal': 'neutral'}
        
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        stoch_k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        stoch_d = stoch_k.rolling(window=d_period).mean()
        
        current_k = float(stoch_k.iloc[-1]) if not np.isnan(stoch_k.iloc[-1]) else 50
        current_d = float(stoch_d.iloc[-1]) if not np.isnan(stoch_d.iloc[-1]) else 50
        
        if current_k > 80 and current_d > 80:
            signal = 'overbought'
        elif current_k < 20 and current_d < 20:
            signal = 'oversold'
        elif current_k > current_d:
            signal = 'bullish'
        elif current_k < current_d:
            signal = 'bearish'
        else:
            signal = 'neutral'
        
        return {
            'k': round(current_k, 2),
            'd': round(current_d, 2),
            'signal': signal
        }
    
    def calculate_ema_set(self, df):
        periods = [9, 21, 50, 100, 200]
        result = {}
        
        for period in periods:
            if len(df) >= period:
                ema = df['close'].ewm(span=period, adjust=False).mean()
                result[f'ema_{period}'] = round(float(ema.iloc[-1]), 5)
            else:
                result[f'ema_{period}'] = None
        
        current_price = float(df['close'].iloc[-1])
        if result.get('ema_50') and result.get('ema_200'):
            if result['ema_50'] > result['ema_200']:
                result['golden_cross'] = True
                result['death_cross'] = False
            else:
                result['golden_cross'] = False
                result['death_cross'] = True
        
        return result
    
    def calculate_sma_set(self, df):
        periods = [10, 20, 50, 100, 200]
        result = {}
        
        for period in periods:
            if len(df) >= period:
                sma = df['close'].rolling(window=period).mean()
                result[f'sma_{period}'] = round(float(sma.iloc[-1]), 5)
            else:
                result[f'sma_{period}'] = None
        
        return result
    
    def calculate_momentum(self, df, period=10):
        if len(df) < period + 1:
            return {'value': 0, 'signal': 'neutral'}
        
        momentum = df['close'].diff(period)
        current_mom = float(momentum.iloc[-1]) if not np.isnan(momentum.iloc[-1]) else 0
        
        if current_mom > 0:
            signal = 'bullish'
        elif current_mom < 0:
            signal = 'bearish'
        else:
            signal = 'neutral'
        
        return {
            'value': round(current_mom, 6),
            'signal': signal
        }
    
    def calculate_obv(self, df):
        if len(df) < 2:
            return {'value': 0, 'trend': 'neutral'}
        
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        obv_series = pd.Series(obv)
        current_obv = float(obv_series.iloc[-1])
        
        if len(obv_series) > 10:
            obv_sma = obv_series.rolling(window=10).mean()
            if current_obv > float(obv_sma.iloc[-1]):
                trend = 'bullish'
            else:
                trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'value': current_obv,
            'trend': trend
        }
    
    def calculate_vwap(self, df):
        if len(df) < 1 or 'volume' not in df.columns:
            return {'value': float(df['close'].iloc[-1]) if len(df) > 0 else 0}
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        
        current_vwap = float(vwap.iloc[-1]) if not np.isnan(vwap.iloc[-1]) else float(df['close'].iloc[-1])
        current_price = float(df['close'].iloc[-1])
        
        if current_price > current_vwap:
            signal = 'above_vwap'
        else:
            signal = 'below_vwap'
        
        return {
            'value': round(current_vwap, 5),
            'signal': signal
        }
    
    def calculate_williams_r(self, df, period=14):
        if len(df) < period:
            return {'value': -50, 'signal': 'neutral'}
        
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        williams_r = -100 * (highest_high - df['close']) / (highest_high - lowest_low)
        current_wr = float(williams_r.iloc[-1]) if not np.isnan(williams_r.iloc[-1]) else -50
        
        if current_wr > -20:
            signal = 'overbought'
        elif current_wr < -80:
            signal = 'oversold'
        else:
            signal = 'neutral'
        
        return {
            'value': round(current_wr, 2),
            'signal': signal
        }
    
    def calculate_cci(self, df, period=20):
        if len(df) < period:
            return {'value': 0, 'signal': 'neutral'}
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mean_dev = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (typical_price - sma) / (0.015 * mean_dev)
        current_cci = float(cci.iloc[-1]) if not np.isnan(cci.iloc[-1]) else 0
        
        if current_cci > 100:
            signal = 'overbought'
        elif current_cci < -100:
            signal = 'oversold'
        else:
            signal = 'neutral'
        
        return {
            'value': round(current_cci, 2),
            'signal': signal
        }
