import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from technical_indicators import TechnicalIndicators
from pattern_detector import PatternDetector
from smc_analyzer import SMCAnalyzer
import json

class TradingEngine:
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.pattern_detector = PatternDetector()
        self.smc_analyzer = SMCAnalyzer()
        
    def analyze_market(self, symbol, data):
        if not data or len(data) < 50:
            return self._empty_analysis(symbol)
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        technical_analysis = self.indicators.calculate_all(df)
        smc_analysis = self.smc_analyzer.analyze(df)
        patterns = self.pattern_detector.detect_all(df)
        
        market_structure = self._analyze_market_structure(df, smc_analysis)
        regime = self._detect_regime(df, technical_analysis)
        
        signals = self._generate_signals(
            symbol, df, technical_analysis, smc_analysis, patterns, market_structure, regime
        )
        
        prediction = self._generate_prediction(df, technical_analysis, smc_analysis, market_structure)
        
        current_price = float(df['close'].iloc[-1])
        price_change = float(df['close'].iloc[-1] - df['close'].iloc[-2]) if len(df) > 1 else 0
        price_change_pct = (price_change / df['close'].iloc[-2] * 100) if len(df) > 1 and df['close'].iloc[-2] != 0 else 0
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'price_change': price_change,
            'price_change_pct': round(price_change_pct, 4),
            'technical': technical_analysis,
            'smc': smc_analysis,
            'patterns': patterns,
            'market_structure': market_structure,
            'regime': regime,
            'signals': signals,
            'prediction': prediction,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _empty_analysis(self, symbol):
        return {
            'symbol': symbol,
            'current_price': 0,
            'price_change': 0,
            'price_change_pct': 0,
            'technical': {},
            'smc': {},
            'patterns': [],
            'market_structure': {'trend': 'unknown', 'structure': 'unknown'},
            'regime': {'type': 'unknown', 'volatility': 'unknown'},
            'signals': [],
            'prediction': {},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _analyze_market_structure(self, df, smc_analysis):
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        
        swing_highs = []
        swing_lows = []
        lookback = 5
        
        for i in range(lookback, len(df) - lookback):
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                swing_highs.append({'index': i, 'price': float(highs[i]), 'timestamp': str(df['timestamp'].iloc[i])})
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                swing_lows.append({'index': i, 'price': float(lows[i]), 'timestamp': str(df['timestamp'].iloc[i])})
        
        trend = 'ranging'
        structure_type = 'uncertain'
        
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            recent_highs = swing_highs[-2:]
            recent_lows = swing_lows[-2:]
            
            hh = recent_highs[-1]['price'] > recent_highs[-2]['price'] if len(recent_highs) >= 2 else False
            hl = recent_lows[-1]['price'] > recent_lows[-2]['price'] if len(recent_lows) >= 2 else False
            lh = recent_highs[-1]['price'] < recent_highs[-2]['price'] if len(recent_highs) >= 2 else False
            ll = recent_lows[-1]['price'] < recent_lows[-2]['price'] if len(recent_lows) >= 2 else False
            
            if hh and hl:
                trend = 'bullish'
                structure_type = 'HH+HL (Bullish Structure)'
            elif lh and ll:
                trend = 'bearish'
                structure_type = 'LH+LL (Bearish Structure)'
            else:
                trend = 'ranging'
                structure_type = 'Consolidation'
        
        bos_detected = False
        choch_detected = False
        
        if len(swing_lows) >= 2 and trend == 'bullish':
            if closes[-1] < swing_lows[-1]['price']:
                bos_detected = True
        elif len(swing_highs) >= 2 and trend == 'bearish':
            if closes[-1] > swing_highs[-1]['price']:
                bos_detected = True
        
        recent_changes = []
        if len(df) > 10:
            for i in range(-10, -1):
                if abs(closes[i] - closes[i-1]) > 2 * df['close'].diff().abs().mean():
                    choch_detected = True
                    recent_changes.append(i)
        
        return {
            'trend': trend,
            'structure': structure_type,
            'swing_highs': swing_highs[-5:] if swing_highs else [],
            'swing_lows': swing_lows[-5:] if swing_lows else [],
            'bos_detected': bos_detected,
            'choch_detected': choch_detected,
            'strength': self._calculate_trend_strength(df)
        }
    
    def _calculate_trend_strength(self, df):
        if len(df) < 20:
            return 0
        
        closes = df['close'].values
        sma20 = np.mean(closes[-20:])
        current = closes[-1]
        
        if sma20 == 0:
            return 0
            
        deviation = (current - sma20) / sma20 * 100
        strength = min(abs(deviation) * 10, 100)
        return round(strength, 2)
    
    def _detect_regime(self, df, technical):
        if len(df) < 20:
            return {'type': 'unknown', 'volatility': 'unknown', 'description': 'Insufficient data'}
        
        atr = technical.get('atr', {}).get('value', 0)
        atr_percent = technical.get('atr', {}).get('percent', 0)
        adx = technical.get('adx', {}).get('value', 0)
        
        if atr_percent > 2:
            volatility = 'high'
        elif atr_percent > 1:
            volatility = 'medium'
        else:
            volatility = 'low'
        
        if adx > 25:
            if volatility == 'high':
                regime_type = 'trending_high_vol'
                description = 'Strong trending market with high volatility - momentum strategies preferred'
            else:
                regime_type = 'trending_low_vol'
                description = 'Steady trending market - trend following strategies work well'
        else:
            if volatility == 'high':
                regime_type = 'ranging_high_vol'
                description = 'Choppy ranging market - be cautious, wait for clearer signals'
            else:
                regime_type = 'ranging_low_vol'
                description = 'Quiet ranging market - mean reversion strategies may work'
        
        return {
            'type': regime_type,
            'volatility': volatility,
            'adx': adx,
            'atr_percent': atr_percent,
            'description': description
        }
    
    def _generate_signals(self, symbol, df, technical, smc, patterns, structure, regime):
        signals = []
        confluence_factors = []
        
        rsi = technical.get('rsi', {}).get('value', 50)
        macd = technical.get('macd', {})
        bb = technical.get('bollinger', {})
        
        if rsi < 30:
            confluence_factors.append({'factor': 'RSI Oversold', 'direction': 'bullish', 'weight': 15})
        elif rsi > 70:
            confluence_factors.append({'factor': 'RSI Overbought', 'direction': 'bearish', 'weight': 15})
        
        if macd.get('histogram', 0) > 0 and macd.get('signal', 'neutral') == 'bullish':
            confluence_factors.append({'factor': 'MACD Bullish', 'direction': 'bullish', 'weight': 20})
        elif macd.get('histogram', 0) < 0 and macd.get('signal', 'neutral') == 'bearish':
            confluence_factors.append({'factor': 'MACD Bearish', 'direction': 'bearish', 'weight': 20})
        
        if structure['trend'] == 'bullish':
            confluence_factors.append({'factor': 'Bullish Structure', 'direction': 'bullish', 'weight': 25})
        elif structure['trend'] == 'bearish':
            confluence_factors.append({'factor': 'Bearish Structure', 'direction': 'bearish', 'weight': 25})
        
        if smc.get('order_blocks'):
            for ob in smc['order_blocks'][-3:]:
                if ob['type'] == 'bullish':
                    confluence_factors.append({'factor': f"Bullish Order Block at {ob['price']:.5f}", 'direction': 'bullish', 'weight': 20})
                else:
                    confluence_factors.append({'factor': f"Bearish Order Block at {ob['price']:.5f}", 'direction': 'bearish', 'weight': 20})
        
        if smc.get('fvgs'):
            for fvg in smc['fvgs'][-3:]:
                if fvg['type'] == 'bullish':
                    confluence_factors.append({'factor': f"Bullish FVG zone", 'direction': 'bullish', 'weight': 15})
                else:
                    confluence_factors.append({'factor': f"Bearish FVG zone", 'direction': 'bearish', 'weight': 15})
        
        if smc.get('liquidity_sweep'):
            confluence_factors.append({'factor': 'Liquidity Sweep Detected', 'direction': smc['liquidity_sweep']['direction'], 'weight': 25})
        
        for pattern in patterns[-3:]:
            if pattern['type'] in ['hammer', 'bullish_engulfing', 'morning_star', 'three_white_soldiers']:
                confluence_factors.append({'factor': f"Bullish Pattern: {pattern['type']}", 'direction': 'bullish', 'weight': 15})
            elif pattern['type'] in ['hanging_man', 'bearish_engulfing', 'evening_star', 'three_black_crows']:
                confluence_factors.append({'factor': f"Bearish Pattern: {pattern['type']}", 'direction': 'bearish', 'weight': 15})
        
        bullish_score = sum(f['weight'] for f in confluence_factors if f['direction'] == 'bullish')
        bearish_score = sum(f['weight'] for f in confluence_factors if f['direction'] == 'bearish')
        
        total_factors = len(confluence_factors)
        
        if bullish_score > bearish_score and bullish_score >= 30:
            direction = 'long'
            score = bullish_score
            grade = self._calculate_grade(bullish_score, total_factors)
            confidence = min(bullish_score / 100, 0.95)
        elif bearish_score > bullish_score and bearish_score >= 30:
            direction = 'short'
            score = bearish_score
            grade = self._calculate_grade(bearish_score, total_factors)
            confidence = min(bearish_score / 100, 0.95)
        else:
            return signals
        
        current_price = float(df['close'].iloc[-1])
        atr = technical.get('atr', {}).get('value', current_price * 0.001)
        
        if direction == 'long':
            stop_loss = current_price - (2 * atr)
            take_profit = current_price + (3 * atr)
        else:
            stop_loss = current_price + (2 * atr)
            take_profit = current_price - (3 * atr)
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        reasoning = self._generate_reasoning(direction, grade, confluence_factors, structure, regime)
        
        signal = {
            'symbol': symbol,
            'signal_type': 'confluence',
            'direction': direction,
            'grade': grade,
            'confidence': round(confidence, 2),
            'score': score,
            'entry_price': current_price,
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'risk_reward': round(risk_reward, 2),
            'contributors': confluence_factors,
            'reasoning': reasoning,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        signals.append(signal)
        return signals
    
    def _calculate_grade(self, score, factor_count):
        if score >= 80 and factor_count >= 6:
            return 'S'
        elif score >= 65 and factor_count >= 5:
            return 'A'
        elif score >= 50 and factor_count >= 4:
            return 'B'
        elif score >= 35 and factor_count >= 3:
            return 'C'
        elif score >= 20:
            return 'D'
        else:
            return 'E'
    
    def _generate_reasoning(self, direction, grade, factors, structure, regime):
        action = "BUY" if direction == 'long' else "SELL"
        factor_list = [f['factor'] for f in factors if f['direction'] == ('bullish' if direction == 'long' else 'bearish')]
        
        reasoning = f"**{grade}-Grade {action} Signal**\n\n"
        reasoning += f"**Market Structure:** {structure['structure']} ({structure['trend'].upper()} bias)\n\n"
        reasoning += f"**Regime:** {regime['description']}\n\n"
        reasoning += f"**Confluence Factors ({len(factor_list)}):**\n"
        
        for factor in factor_list:
            reasoning += f"  - {factor}\n"
        
        if grade in ['S', 'A']:
            reasoning += f"\n**Recommendation:** Strong setup with high confluence. Consider full position size."
        elif grade == 'B':
            reasoning += f"\n**Recommendation:** Good setup. Consider standard position size."
        elif grade == 'C':
            reasoning += f"\n**Recommendation:** Moderate setup. Consider reduced position size or wait for better entry."
        else:
            reasoning += f"\n**Recommendation:** Weak setup. Skip or monitor only."
        
        return reasoning
    
    def _generate_prediction(self, df, technical, smc, structure):
        if len(df) < 20:
            return {}
        
        current_price = float(df['close'].iloc[-1])
        atr = technical.get('atr', {}).get('value', current_price * 0.001)
        
        trend_bias = 1 if structure['trend'] == 'bullish' else (-1 if structure['trend'] == 'bearish' else 0)
        
        median_target = current_price + (trend_bias * 1.5 * atr)
        upper_target = current_price + (2.5 * atr)
        lower_target = current_price - (2.5 * atr)
        
        bullish_prob = 0.5
        bearish_prob = 0.5
        neutral_prob = 0.15
        
        if structure['trend'] == 'bullish':
            bullish_prob = 0.55 + (structure['strength'] / 500)
            bearish_prob = 0.30 - (structure['strength'] / 500)
        elif structure['trend'] == 'bearish':
            bearish_prob = 0.55 + (structure['strength'] / 500)
            bullish_prob = 0.30 - (structure['strength'] / 500)
        
        total = bullish_prob + bearish_prob + neutral_prob
        bullish_prob /= total
        bearish_prob /= total
        neutral_prob /= total
        
        return {
            'median_target': round(median_target, 5),
            'upper_bound': round(upper_target, 5),
            'lower_bound': round(lower_target, 5),
            'scenarios': {
                'bullish': {
                    'probability': round(bullish_prob * 100, 1),
                    'target': round(current_price + (2 * atr), 5),
                    'description': f"Price rallies to {round(current_price + (2 * atr), 5)}"
                },
                'neutral': {
                    'probability': round(neutral_prob * 100, 1),
                    'target': round(current_price, 5),
                    'description': f"Price consolidates around {round(current_price, 5)}"
                },
                'bearish': {
                    'probability': round(bearish_prob * 100, 1),
                    'target': round(current_price - (2 * atr), 5),
                    'description': f"Price drops to {round(current_price - (2 * atr), 5)}"
                }
            },
            'timeframe': '4-8 hours',
            'confidence': round(max(bullish_prob, bearish_prob) * 100, 1)
        }
    
    def generate_live_narration(self, symbol, data):
        if not data or len(data) < 10:
            return self._empty_narration(symbol)
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        current_price = float(df['close'].iloc[-1])
        prev_price = float(df['close'].iloc[-2]) if len(df) > 1 else current_price
        price_change = current_price - prev_price
        
        technical = self.indicators.calculate_all(df)
        smc = self.smc_analyzer.analyze(df)
        structure = self._analyze_market_structure(df, smc)
        
        rsi = technical.get('rsi', {}).get('value', 50)
        macd_hist = technical.get('macd', {}).get('histogram', 0)
        
        narration = f"**{symbol} Live Analysis** (Updated: {datetime.utcnow().strftime('%H:%M:%S UTC')})\n\n"
        narration += f"**Current Price:** {current_price:.5f} "
        narration += f"({'↑' if price_change > 0 else '↓'} {abs(price_change):.5f} pips)\n\n"
        
        narration += f"**What's Happening:**\n"
        
        if structure['trend'] == 'bullish':
            narration += f"- Price is in a BULLISH structure (Higher Highs + Higher Lows)\n"
        elif structure['trend'] == 'bearish':
            narration += f"- Price is in a BEARISH structure (Lower Highs + Lower Lows)\n"
        else:
            narration += f"- Price is RANGING between key levels\n"
        
        if rsi > 70:
            narration += f"- RSI at {rsi:.1f} - OVERBOUGHT (potential pullback)\n"
        elif rsi < 30:
            narration += f"- RSI at {rsi:.1f} - OVERSOLD (potential bounce)\n"
        else:
            narration += f"- RSI at {rsi:.1f} - neutral momentum\n"
        
        if macd_hist > 0:
            narration += f"- MACD histogram positive - bullish momentum building\n"
        else:
            narration += f"- MACD histogram negative - bearish pressure\n"
        
        if smc.get('order_blocks'):
            ob = smc['order_blocks'][-1]
            narration += f"- Key Order Block at {ob['price']:.5f} ({ob['type']})\n"
        
        if smc.get('fvgs'):
            fvg = smc['fvgs'][-1]
            narration += f"- Fair Value Gap detected ({fvg['type']})\n"
        
        narration += f"\n**What We're Watching:**\n"
        
        if structure['swing_highs']:
            nearest_high = structure['swing_highs'][-1]['price']
            narration += f"- Resistance at {nearest_high:.5f}\n"
        
        if structure['swing_lows']:
            nearest_low = structure['swing_lows'][-1]['price']
            narration += f"- Support at {nearest_low:.5f}\n"
        
        prediction = self._generate_prediction(df, technical, smc, structure)
        
        narration += f"\n**Prediction (Next 4-8 hours):**\n"
        for scenario, details in prediction.get('scenarios', {}).items():
            narration += f"- {scenario.upper()}: {details['probability']}% probability → {details['description']}\n"
        
        return {
            'symbol': symbol,
            'narration': narration,
            'current_price': current_price,
            'price_change': price_change,
            'structure': structure,
            'technical_summary': {
                'rsi': rsi,
                'macd_histogram': macd_hist,
                'trend': structure['trend']
            },
            'prediction': prediction,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _empty_narration(self, symbol):
        return {
            'symbol': symbol,
            'narration': f"**{symbol}** - Waiting for market data...",
            'current_price': 0,
            'price_change': 0,
            'structure': {},
            'technical_summary': {},
            'prediction': {},
            'timestamp': datetime.utcnow().isoformat()
        }
