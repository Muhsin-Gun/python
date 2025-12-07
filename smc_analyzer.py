import numpy as np
import pandas as pd
from datetime import datetime

class SMCAnalyzer:
    def analyze(self, df):
        if len(df) < 20:
            return {}
        
        result = {
            'order_blocks': self.detect_order_blocks(df),
            'fvgs': self.detect_fair_value_gaps(df),
            'liquidity_zones': self.detect_liquidity_zones(df),
            'supply_demand': self.detect_supply_demand_zones(df),
            'breaker_blocks': self.detect_breaker_blocks(df),
            'liquidity_sweep': self.detect_liquidity_sweep(df),
            'displacement': self.detect_displacement(df),
            'session_analysis': self.analyze_sessions(df)
        }
        
        return result
    
    def detect_order_blocks(self, df):
        order_blocks = []
        
        if len(df) < 10:
            return order_blocks
        
        for i in range(3, len(df) - 1):
            curr_close = float(df['close'].iloc[i])
            curr_open = float(df['open'].iloc[i])
            curr_high = float(df['high'].iloc[i])
            curr_low = float(df['low'].iloc[i])
            
            next_close = float(df['close'].iloc[i + 1]) if i + 1 < len(df) else curr_close
            next_open = float(df['open'].iloc[i + 1]) if i + 1 < len(df) else curr_open
            next_high = float(df['high'].iloc[i + 1]) if i + 1 < len(df) else curr_high
            next_low = float(df['low'].iloc[i + 1]) if i + 1 < len(df) else curr_low
            
            prev_close = float(df['close'].iloc[i - 1])
            prev_open = float(df['open'].iloc[i - 1])
            
            curr_body = abs(curr_close - curr_open)
            next_body = abs(next_close - next_open)
            prev_body = abs(prev_close - prev_open)
            
            avg_body = (curr_body + prev_body) / 2
            
            if next_body > 1.5 * avg_body and next_close > next_open:
                if curr_close < curr_open:
                    order_blocks.append({
                        'type': 'bullish',
                        'index': i,
                        'price': float(curr_low),
                        'high': float(curr_high),
                        'low': float(curr_low),
                        'timestamp': str(df['timestamp'].iloc[i]),
                        'strength': 'strong' if next_body > 2 * avg_body else 'moderate',
                        'status': 'fresh',
                        'description': 'Bullish Order Block - institutional buying zone'
                    })
            
            if next_body > 1.5 * avg_body and next_close < next_open:
                if curr_close > curr_open:
                    order_blocks.append({
                        'type': 'bearish',
                        'index': i,
                        'price': float(curr_high),
                        'high': float(curr_high),
                        'low': float(curr_low),
                        'timestamp': str(df['timestamp'].iloc[i]),
                        'strength': 'strong' if next_body > 2 * avg_body else 'moderate',
                        'status': 'fresh',
                        'description': 'Bearish Order Block - institutional selling zone'
                    })
        
        return order_blocks[-10:] if order_blocks else []
    
    def detect_fair_value_gaps(self, df):
        fvgs = []
        
        if len(df) < 5:
            return fvgs
        
        for i in range(1, len(df) - 1):
            prev_high = float(df['high'].iloc[i - 1])
            prev_low = float(df['low'].iloc[i - 1])
            curr_high = float(df['high'].iloc[i])
            curr_low = float(df['low'].iloc[i])
            next_high = float(df['high'].iloc[i + 1])
            next_low = float(df['low'].iloc[i + 1])
            
            if curr_low > prev_high:
                gap_size = curr_low - prev_high
                fvgs.append({
                    'type': 'bullish',
                    'index': i,
                    'gap_top': float(curr_low),
                    'gap_bottom': float(prev_high),
                    'gap_size': gap_size,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'filled': next_low <= prev_high,
                    'description': f'Bullish FVG - gap zone {prev_high:.5f} to {curr_low:.5f}'
                })
            
            if curr_high < prev_low:
                gap_size = prev_low - curr_high
                fvgs.append({
                    'type': 'bearish',
                    'index': i,
                    'gap_top': float(prev_low),
                    'gap_bottom': float(curr_high),
                    'gap_size': gap_size,
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'filled': next_high >= prev_low,
                    'description': f'Bearish FVG - gap zone {curr_high:.5f} to {prev_low:.5f}'
                })
        
        return fvgs[-10:] if fvgs else []
    
    def detect_liquidity_zones(self, df):
        zones = []
        
        if len(df) < 20:
            return zones
        
        highs = df['high'].values
        lows = df['low'].values
        
        swing_highs = []
        swing_lows = []
        lookback = 5
        
        for i in range(lookback, len(df) - lookback):
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                swing_highs.append({'index': i, 'price': float(highs[i])})
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                swing_lows.append({'index': i, 'price': float(lows[i])})
        
        for sh in swing_highs[-5:]:
            zones.append({
                'type': 'sell_side_liquidity',
                'level': sh['price'],
                'index': sh['index'],
                'timestamp': str(df['timestamp'].iloc[sh['index']]),
                'description': f'Sell-side liquidity above {sh["price"]:.5f} - stops resting above'
            })
        
        for sl in swing_lows[-5:]:
            zones.append({
                'type': 'buy_side_liquidity',
                'level': sl['price'],
                'index': sl['index'],
                'timestamp': str(df['timestamp'].iloc[sl['index']]),
                'description': f'Buy-side liquidity below {sl["price"]:.5f} - stops resting below'
            })
        
        closes = df['close'].values
        price_range = max(closes) - min(closes)
        
        round_levels = []
        base_price = min(closes)
        increment = price_range / 10
        
        for i in range(11):
            level = base_price + (i * increment)
            rounded = round(level, 2 if level > 10 else 4)
            if rounded not in round_levels:
                round_levels.append(rounded)
                zones.append({
                    'type': 'psychological_level',
                    'level': rounded,
                    'description': f'Psychological level at {rounded}'
                })
        
        return zones
    
    def detect_supply_demand_zones(self, df):
        zones = []
        
        if len(df) < 20:
            return zones
        
        for i in range(10, len(df) - 3):
            window = df.iloc[i-5:i+1]
            
            consolidation_range = window['high'].max() - window['low'].min()
            avg_body = abs(window['close'] - window['open']).mean()
            
            if consolidation_range < avg_body * 3:
                next_move = float(df['close'].iloc[i+3]) - float(df['close'].iloc[i])
                
                if next_move > consolidation_range * 1.5:
                    zones.append({
                        'type': 'demand',
                        'zone_high': float(window['high'].max()),
                        'zone_low': float(window['low'].min()),
                        'index': i,
                        'timestamp': str(df['timestamp'].iloc[i]),
                        'strength': 'strong' if next_move > consolidation_range * 2 else 'moderate',
                        'status': 'fresh',
                        'description': 'Demand Zone - accumulation area before rally'
                    })
                
                elif next_move < -consolidation_range * 1.5:
                    zones.append({
                        'type': 'supply',
                        'zone_high': float(window['high'].max()),
                        'zone_low': float(window['low'].min()),
                        'index': i,
                        'timestamp': str(df['timestamp'].iloc[i]),
                        'strength': 'strong' if next_move < -consolidation_range * 2 else 'moderate',
                        'status': 'fresh',
                        'description': 'Supply Zone - distribution area before drop'
                    })
        
        return zones[-10:] if zones else []
    
    def detect_breaker_blocks(self, df):
        breakers = []
        order_blocks = self.detect_order_blocks(df)
        
        current_price = float(df['close'].iloc[-1])
        
        for ob in order_blocks:
            if ob['type'] == 'bullish' and current_price < ob['low']:
                breakers.append({
                    'type': 'bearish_breaker',
                    'original_type': 'bullish',
                    'price': ob['price'],
                    'high': ob['high'],
                    'low': ob['low'],
                    'index': ob['index'],
                    'timestamp': ob['timestamp'],
                    'description': 'Failed bullish OB now acting as resistance'
                })
            elif ob['type'] == 'bearish' and current_price > ob['high']:
                breakers.append({
                    'type': 'bullish_breaker',
                    'original_type': 'bearish',
                    'price': ob['price'],
                    'high': ob['high'],
                    'low': ob['low'],
                    'index': ob['index'],
                    'timestamp': ob['timestamp'],
                    'description': 'Failed bearish OB now acting as support'
                })
        
        return breakers
    
    def detect_liquidity_sweep(self, df):
        if len(df) < 10:
            return None
        
        recent = df.iloc[-5:]
        
        for i in range(len(recent) - 1):
            curr_high = float(recent['high'].iloc[i])
            curr_low = float(recent['low'].iloc[i])
            curr_close = float(recent['close'].iloc[i])
            curr_open = float(recent['open'].iloc[i])
            
            wick_up = curr_high - max(curr_open, curr_close)
            wick_down = min(curr_open, curr_close) - curr_low
            body = abs(curr_close - curr_open)
            
            avg_range = (df['high'] - df['low']).mean()
            
            if wick_up > 2 * body and wick_up > avg_range * 0.5:
                return {
                    'type': 'upside_sweep',
                    'direction': 'bearish',
                    'index': len(df) - 5 + i,
                    'sweep_level': curr_high,
                    'close_level': curr_close,
                    'timestamp': str(recent['timestamp'].iloc[i]),
                    'description': 'Liquidity sweep above highs - bearish reversal likely'
                }
            
            if wick_down > 2 * body and wick_down > avg_range * 0.5:
                return {
                    'type': 'downside_sweep',
                    'direction': 'bullish',
                    'index': len(df) - 5 + i,
                    'sweep_level': curr_low,
                    'close_level': curr_close,
                    'timestamp': str(recent['timestamp'].iloc[i]),
                    'description': 'Liquidity sweep below lows - bullish reversal likely'
                }
        
        return None
    
    def detect_displacement(self, df):
        displacements = []
        
        if len(df) < 5:
            return displacements
        
        avg_body = abs(df['close'] - df['open']).mean()
        
        for i in range(-5, 0):
            if abs(i) >= len(df):
                continue
            
            body = abs(float(df['close'].iloc[i]) - float(df['open'].iloc[i]))
            
            if body > 2 * avg_body:
                direction = 'bullish' if float(df['close'].iloc[i]) > float(df['open'].iloc[i]) else 'bearish'
                displacements.append({
                    'type': 'displacement',
                    'direction': direction,
                    'index': len(df) + i,
                    'body_size': body,
                    'multiplier': round(body / avg_body, 2),
                    'timestamp': str(df['timestamp'].iloc[i]),
                    'description': f'{direction.capitalize()} displacement - {round(body/avg_body, 1)}x average body'
                })
        
        return displacements
    
    def analyze_sessions(self, df):
        if len(df) < 10 or 'timestamp' not in df.columns:
            return {}
        
        try:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        except:
            return {}
        
        asian_mask = (df['hour'] >= 0) & (df['hour'] < 8)
        london_mask = (df['hour'] >= 8) & (df['hour'] < 16)
        ny_mask = (df['hour'] >= 13) & (df['hour'] < 22)
        
        sessions = {}
        
        if asian_mask.sum() > 0:
            asian_data = df[asian_mask]
            sessions['asian'] = {
                'high': float(asian_data['high'].max()),
                'low': float(asian_data['low'].min()),
                'range': float(asian_data['high'].max() - asian_data['low'].min()),
                'description': 'Asian session range - watch for London breakout'
            }
        
        if london_mask.sum() > 0:
            london_data = df[london_mask]
            sessions['london'] = {
                'high': float(london_data['high'].max()),
                'low': float(london_data['low'].min()),
                'range': float(london_data['high'].max() - london_data['low'].min()),
                'description': 'London session - higher volatility expected'
            }
        
        if ny_mask.sum() > 0:
            ny_data = df[ny_mask]
            sessions['new_york'] = {
                'high': float(ny_data['high'].max()),
                'low': float(ny_data['low'].min()),
                'range': float(ny_data['high'].max() - ny_data['low'].min()),
                'description': 'New York session - watch for directional moves'
            }
        
        return sessions
