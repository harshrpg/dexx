import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

class TechnicalAnalysisService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_indicators(self, ohlcv_data: List[Dict]) -> Dict:
        """Calculate technical indicators from OHLCV data.
        
        Args:
            ohlcv_data: List of dictionaries containing OHLCV data
            
        Returns:
            Dictionary containing calculated indicators
        """
        try:
            # Convert to pandas DataFrame
            df = pd.DataFrame.from_records(ohlcv_data)
            # Convert milliseconds to datetime
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time', inplace=True)
            
            # Calculate indicators
            indicators = {
                'trend': self._calculate_trend(df),
                'rsi': self._calculate_rsi(df),
                'macd': self._calculate_macd(df),
                'bollinger_bands': self._calculate_bollinger_bands(df),
                'moving_averages': self._calculate_moving_averages(df),
                'support_resistance': self._calculate_support_resistance(df)
            }
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}", exc_info=True)
            raise

    def _calculate_trend(self, df: pd.DataFrame) -> Dict:
        """Calculate trend using multiple timeframes."""
        try:
            # Calculate 20, 50, and 200-day moving averages
            ma20 = df['close'].rolling(window=20).mean()
            ma50 = df['close'].rolling(window=50).mean()
            ma200 = df['close'].rolling(window=200).mean()
            
            current_price = df['close'].iloc[-1]
            
            trend = {
                'direction': 'bullish' if current_price > ma20.iloc[-1] > ma50.iloc[-1] > ma200.iloc[-1] else 'bearish',
                'strength': 'strong' if abs(current_price - ma20.iloc[-1]) / ma20.iloc[-1] > 0.02 else 'weak',
                'ma20': ma20.iloc[-1],
                'ma50': ma50.iloc[-1],
                'ma200': ma200.iloc[-1]
            }
            
            return trend
            
        except Exception as e:
            self.logger.error(f"Error calculating trend: {str(e)}", exc_info=True)
            raise

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """Calculate Relative Strength Index using Wilder's smoothing method (matching TradingView)."""
        try:
            # Calculate price changes
            delta = df['close'].diff()
            
            # Calculate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)

             # Create result Series initialized with NaNs
            rsi = pd.Series(index=df.index)
            
            # We need at least period+1 data points to calculate first RSI value
            if len(df) <= period:
                return {
                    'value': np.nan,
                    'signal': 'neutral',
                    'trend': 'neutral'
                }
            
            # First average (SMA for initial period)
            first_avg_gain = gains.iloc[:period].mean()
            first_avg_loss = losses.iloc[:period].mean()

            if first_avg_loss == 0:
                rsi.iloc[period] = 100
            else:
                rs = first_avg_gain / first_avg_loss
                rsi.iloc[period] = 100 - (100 / (1 + rs))
            
            # Calculate RSI using Wilder's smoothing method
            avg_gain = first_avg_gain
            avg_loss = first_avg_loss
            
            # Initialize smoothed averages list with first values
            smoothed_gains = [first_avg_gain]
            smoothed_losses = [first_avg_loss]
            
            # Calculate subsequent averages using Wilder's smoothing (α = 1/period)
            # Formula: avg_gain = (previous_avg_gain * (period - 1) + current_gain) / period
            for idx in range(period + 1, len(df)):
                current_gain = gains.iloc[idx]
                current_loss = losses.iloc[idx]
                
                # Apply Wilder's smoothing formula
                avg_gain = ((avg_gain * (period - 1)) + current_gain) / period
                avg_loss = ((avg_loss * (period - 1)) + current_loss) / period
                
                # Calculate RSI
                if avg_loss == 0:
                    rsi.iloc[idx] = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi.iloc[idx] = 100 - (100 / (1 + rs))
        
            current_rsi = rsi.iloc[-1]
            
            return {
                'value': current_rsi,
                'signal': 'overbought' if current_rsi > 70 else 'oversold' if current_rsi < 30 else 'neutral',
                'trend': 'bullish' if current_rsi > 50 else 'bearish'
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}", exc_info=True)
            raise

    def _calculate_macd(self, df: pd.DataFrame) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence).
        Fast length: 12
        Slow length: 26
        Signal length: 9
        Source: Close price
        """
        try:
            # Calculate EMAs
            fast_ema = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
            slow_ema = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
            
            # Calculate MACD line
            macd_line = fast_ema - slow_ema
            
            # Calculate Signal line with 9-period EMA of MACD
            signal_line = macd_line.ewm(span=9, adjust=False, min_periods=9).mean()
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            # Get latest values
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_hist = histogram.iloc[-1]
            
            # Determine trend and crossover
            trend = 'bullish' if current_macd > current_signal else 'bearish'
            
            # Check for crossover in last 2 periods
            crossover = 'none'
            if len(histogram) >= 2:
                if histogram.iloc[-2] < 0 and histogram.iloc[-1] > 0:
                    crossover = 'bullish'
                elif histogram.iloc[-2] > 0 and histogram.iloc[-1] < 0:
                    crossover = 'bearish'
            
            return {
                'macd': current_macd,
                'signal': current_signal,
                'histogram': current_hist,
                'trend': trend,
                'crossover': crossover
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}", exc_info=True)
            raise

    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict:
        """Calculate Bollinger Bands."""
        try:
            ma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            
            upper_band = ma + (std * std_dev)
            lower_band = ma - (std * std_dev)
            
            current_price = df['close'].iloc[-1]
            
            return {
                'upper': upper_band.iloc[-1],
                'middle': ma.iloc[-1],
                'lower': lower_band.iloc[-1],
                'bandwidth': (upper_band.iloc[-1] - lower_band.iloc[-1]) / ma.iloc[-1],
                'position': 'upper' if current_price > upper_band.iloc[-1] else 'lower' if current_price < lower_band.iloc[-1] else 'middle'
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}", exc_info=True)
            raise

    def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """Calculate various moving averages."""
        try:
            periods = [20, 50, 200]
            mas = {}
            
            for period in periods:
                mas[f'ma{period}'] = df['close'].rolling(window=period).mean().iloc[-1]
            
            return mas
            
        except Exception as e:
            self.logger.error(f"Error calculating moving averages: {str(e)}", exc_info=True)
            raise

    def _calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate support and resistance levels."""
        try:
            recent_data = df.tail(window)
            
            # Find local minima and maxima
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            
            # Simple support/resistance calculation
            resistance = np.max(highs)
            support = np.min(lows)
            
            current_price = df['close'].iloc[-1]
            
            return {
                'support': support,
                'resistance': resistance,
                'distance_to_support': (current_price - support) / current_price,
                'distance_to_resistance': (resistance - current_price) / current_price
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating support/resistance: {str(e)}", exc_info=True)
            raise 