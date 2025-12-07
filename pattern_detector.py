import numpy as np
import pandas as pd
from datetime import datetime

class PatternDetector:
    def detect_all(self, df):
        if len(df) < 10:
            return []
        
        patterns = []
        
        patterns.extend(self.detect_single_candle_patterns(df))
        patterns.extend(self.detect_double_candle_patterns(df))
        patterns.extend(self.detect_triple_candle_patterns(df))
        patterns.extend(self.detect_chart_patterns(df))
        
        return patterns
    
    def detect_single_candle_patterns(self, df):
        patterns = []
        
        for i in range(-5, 0):
            if abs(i) > len(df):
                continue
                
            o = float(df['open'].iloc[i])
            h = float(df['high'].iloc[i])
            l = float(df['low'].iloc[i])
            c = float(df['close'].iloc[i])
            
            body = abs(c - o)
            upper_wick = h - max(o, c)
            lower_wick = min(o, c) - l
            total_range = h - l
            
            if total_range == 0:
                continue
            
            body_ratio = body / total_range
            
            if lower_wick > 2 * body and upper_wick < body * 0.5 and c > o:
                patterns.append({
                    'type': 'hammer',
                    'index': len(df) + i,
                    'price': c,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'strong' if lower_wick > 3 * body else 'moderate',
                    'description': 'Hammer pattern - potential bullish reversal'
                })
            
            if lower_wick > 2 * body and upper_wick < body * 0.5 and c < o:
                patterns.append({
                    'type': 'hanging_man',
                    'index': len(df) + i,
                    'price': c,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'strong' if lower_wick > 3 * body else 'moderate',
                    'description': 'Hanging Man - potential bearish reversal'
                })
            
            if upper_wick > 2 * body and lower_wick < body * 0.5 and c < o:
                patterns.append({
                    'type': 'shooting_star',
                    'index': len(df) + i,
                    'price': c,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'strong' if upper_wick > 3 * body else 'moderate',
                    'description': 'Shooting Star - potential bearish reversal'
                })
            
            if upper_wick > 2 * body and lower_wick < body * 0.5 and c > o:
                patterns.append({
                    'type': 'inverted_hammer',
                    'index': len(df) + i,
                    'price': c,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'strong' if upper_wick > 3 * body else 'moderate',
                    'description': 'Inverted Hammer - potential bullish reversal'
                })
            
            if body_ratio < 0.1 and upper_wick > 0 and lower_wick > 0:
                patterns.append({
                    'type': 'doji',
                    'index': len(df) + i,
                    'price': c,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'neutral',
                    'strength': 'moderate',
                    'description': 'Doji - market indecision, potential reversal'
                })
            
            if body_ratio > 0.8 and upper_wick < body * 0.05 and lower_wick < body * 0.05:
                direction = 'bullish' if c > o else 'bearish'
                patterns.append({
                    'type': 'marubozu',
                    'index': len(df) + i,
                    'price': c,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': direction,
                    'strength': 'strong',
                    'description': f'Marubozu - strong {direction} momentum'
                })
        
        return patterns
    
    def detect_double_candle_patterns(self, df):
        patterns = []
        
        for i in range(-4, 0):
            if abs(i) >= len(df) or abs(i-1) >= len(df):
                continue
            
            o1, h1, l1, c1 = float(df['open'].iloc[i-1]), float(df['high'].iloc[i-1]), float(df['low'].iloc[i-1]), float(df['close'].iloc[i-1])
            o2, h2, l2, c2 = float(df['open'].iloc[i]), float(df['high'].iloc[i]), float(df['low'].iloc[i]), float(df['close'].iloc[i])
            
            body1 = abs(c1 - o1)
            body2 = abs(c2 - o2)
            
            if c1 < o1 and c2 > o2 and c2 > o1 and o2 < c1:
                patterns.append({
                    'type': 'bullish_engulfing',
                    'index': len(df) + i,
                    'price': c2,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'strong' if body2 > 1.5 * body1 else 'moderate',
                    'description': 'Bullish Engulfing - strong reversal signal'
                })
            
            if c1 > o1 and c2 < o2 and c2 < o1 and o2 > c1:
                patterns.append({
                    'type': 'bearish_engulfing',
                    'index': len(df) + i,
                    'price': c2,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'strong' if body2 > 1.5 * body1 else 'moderate',
                    'description': 'Bearish Engulfing - strong reversal signal'
                })
            
            if c1 < o1 and c2 > o2 and body2 < body1 * 0.5 and o2 > c1 and c2 < o1:
                patterns.append({
                    'type': 'bullish_harami',
                    'index': len(df) + i,
                    'price': c2,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'moderate',
                    'description': 'Bullish Harami - potential reversal'
                })
            
            if c1 > o1 and c2 < o2 and body2 < body1 * 0.5 and o2 < c1 and c2 > o1:
                patterns.append({
                    'type': 'bearish_harami',
                    'index': len(df) + i,
                    'price': c2,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'moderate',
                    'description': 'Bearish Harami - potential reversal'
                })
            
            if abs(h1 - h2) < body1 * 0.1 and abs(h1 - h2) < body2 * 0.1:
                patterns.append({
                    'type': 'tweezer_top',
                    'index': len(df) + i,
                    'price': max(h1, h2),
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'moderate',
                    'description': 'Tweezer Top - potential bearish reversal'
                })
            
            if abs(l1 - l2) < body1 * 0.1 and abs(l1 - l2) < body2 * 0.1:
                patterns.append({
                    'type': 'tweezer_bottom',
                    'index': len(df) + i,
                    'price': min(l1, l2),
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'moderate',
                    'description': 'Tweezer Bottom - potential bullish reversal'
                })
        
        return patterns
    
    def detect_triple_candle_patterns(self, df):
        patterns = []
        
        for i in range(-3, 0):
            if abs(i) >= len(df) or abs(i-1) >= len(df) or abs(i-2) >= len(df):
                continue
            
            o1, h1, l1, c1 = float(df['open'].iloc[i-2]), float(df['high'].iloc[i-2]), float(df['low'].iloc[i-2]), float(df['close'].iloc[i-2])
            o2, h2, l2, c2 = float(df['open'].iloc[i-1]), float(df['high'].iloc[i-1]), float(df['low'].iloc[i-1]), float(df['close'].iloc[i-1])
            o3, h3, l3, c3 = float(df['open'].iloc[i]), float(df['high'].iloc[i]), float(df['low'].iloc[i]), float(df['close'].iloc[i])
            
            body1 = abs(c1 - o1)
            body2 = abs(c2 - o2)
            body3 = abs(c3 - o3)
            
            if c1 < o1 and body2 < body1 * 0.3 and c3 > o3 and c3 > (o1 + c1) / 2:
                patterns.append({
                    'type': 'morning_star',
                    'index': len(df) + i,
                    'price': c3,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'strong',
                    'description': 'Morning Star - strong bullish reversal pattern'
                })
            
            if c1 > o1 and body2 < body1 * 0.3 and c3 < o3 and c3 < (o1 + c1) / 2:
                patterns.append({
                    'type': 'evening_star',
                    'index': len(df) + i,
                    'price': c3,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'strong',
                    'description': 'Evening Star - strong bearish reversal pattern'
                })
            
            if c1 > o1 and c2 > o2 and c3 > o3 and o2 > c1 * 0.98 and o3 > c2 * 0.98:
                patterns.append({
                    'type': 'three_white_soldiers',
                    'index': len(df) + i,
                    'price': c3,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bullish',
                    'strength': 'strong',
                    'description': 'Three White Soldiers - strong bullish continuation'
                })
            
            if c1 < o1 and c2 < o2 and c3 < o3 and o2 < c1 * 1.02 and o3 < c2 * 1.02:
                patterns.append({
                    'type': 'three_black_crows',
                    'index': len(df) + i,
                    'price': c3,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'direction': 'bearish',
                    'strength': 'strong',
                    'description': 'Three Black Crows - strong bearish continuation'
                })
        
        return patterns
    
    def detect_chart_patterns(self, df):
        patterns = []
        
        if len(df) < 30:
            return patterns
        
        highs = df['high'].values[-30:]
        lows = df['low'].values[-30:]
        
        resistance_touches = 0
        support_touches = 0
        resistance_level = max(highs)
        support_level = min(lows)
        
        for i, h in enumerate(highs):
            if h >= resistance_level * 0.998:
                resistance_touches += 1
        for i, l in enumerate(lows):
            if l <= support_level * 1.002:
                support_touches += 1
        
        if resistance_touches >= 2 and support_touches >= 2:
            patterns.append({
                'type': 'range',
                'resistance': float(resistance_level),
                'support': float(support_level),
                'timestamp': str(df['timestamp'].iloc[-1]),
                'direction': 'neutral',
                'strength': 'moderate',
                'description': f'Trading Range between {support_level:.5f} and {resistance_level:.5f}'
            })
        
        if len(df) >= 20:
            recent_highs = []
            recent_lows = []
            
            for i in range(5, len(df) - 5):
                if df['high'].iloc[i] == max(df['high'].iloc[i-5:i+5]):
                    recent_highs.append({'idx': i, 'price': float(df['high'].iloc[i])})
                if df['low'].iloc[i] == min(df['low'].iloc[i-5:i+5]):
                    recent_lows.append({'idx': i, 'price': float(df['low'].iloc[i])})
            
            if len(recent_highs) >= 2 and len(recent_lows) >= 2:
                high_trend = recent_highs[-1]['price'] - recent_highs[0]['price']
                low_trend = recent_lows[-1]['price'] - recent_lows[0]['price']
                
                if high_trend < 0 and low_trend > 0:
                    patterns.append({
                        'type': 'triangle_symmetric',
                        'timestamp': str(df['timestamp'].iloc[-1]),
                        'direction': 'neutral',
                        'strength': 'moderate',
                        'description': 'Symmetric Triangle - breakout imminent'
                    })
                elif high_trend < 0 and abs(low_trend) < abs(high_trend) * 0.3:
                    patterns.append({
                        'type': 'triangle_descending',
                        'timestamp': str(df['timestamp'].iloc[-1]),
                        'direction': 'bearish',
                        'strength': 'moderate',
                        'description': 'Descending Triangle - bearish breakout likely'
                    })
                elif low_trend > 0 and abs(high_trend) < abs(low_trend) * 0.3:
                    patterns.append({
                        'type': 'triangle_ascending',
                        'timestamp': str(df['timestamp'].iloc[-1]),
                        'direction': 'bullish',
                        'strength': 'moderate',
                        'description': 'Ascending Triangle - bullish breakout likely'
                    })
        
        return patterns
