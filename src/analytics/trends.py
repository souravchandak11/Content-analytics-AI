"""
Content Analytics Platform - Trend Analysis
============================================
Time-series analysis and trend detection.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from loguru import logger


class TrendAnalyzer:
    """
    Time-series trend analysis for social media metrics.
    """
    
    @staticmethod
    def calculate_trend(
        data: List[Dict],
        metric_key: str,
        date_key: str = 'date'
    ) -> Dict[str, Any]:
        """
        Calculate trend direction and strength.
        
        Args:
            data: List of data points with date and metric
            metric_key: Key for the metric value
            date_key: Key for the date value
            
        Returns:
            Trend analysis results
        """
        if len(data) < 3:
            return {'error': 'Insufficient data points'}
        
        df = pd.DataFrame(data)
        df[date_key] = pd.to_datetime(df[date_key])
        df = df.sort_values(date_key)
        
        values = df[metric_key].values
        x = np.arange(len(values))
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Calculate trend direction
        if slope > 0 and p_value < 0.05:
            direction = 'upward'
        elif slope < 0 and p_value < 0.05:
            direction = 'downward'
        else:
            direction = 'stable'
        
        # Calculate percentage change
        if len(values) > 1 and values[0] != 0:
            pct_change = ((values[-1] - values[0]) / values[0]) * 100
        else:
            pct_change = 0
        
        return {
            'direction': direction,
            'slope': round(slope, 4),
            'r_squared': round(r_value ** 2, 4),
            'p_value': round(p_value, 4),
            'confidence': 'high' if p_value < 0.01 else 'medium' if p_value < 0.05 else 'low',
            'percentage_change': round(pct_change, 2),
            'start_value': float(values[0]),
            'end_value': float(values[-1]),
            'data_points': len(values)
        }
    
    @staticmethod
    def detect_anomalies(
        data: List[float],
        threshold: float = 2.0
    ) -> List[int]:
        """
        Detect anomalies using Z-score method.
        
        Args:
            data: List of values
            threshold: Z-score threshold (default 2.0 = ~95th percentile)
            
        Returns:
            List of anomaly indices
        """
        if len(data) < 3:
            return []
        
        arr = np.array(data)
        mean = np.mean(arr)
        std = np.std(arr)
        
        if std == 0:
            return []
        
        z_scores = np.abs((arr - mean) / std)
        anomalies = np.where(z_scores > threshold)[0].tolist()
        
        return anomalies
    
    @staticmethod
    def moving_average(
        data: List[float],
        window: int = 7
    ) -> List[float]:
        """Calculate simple moving average."""
        if len(data) < window:
            return data
        
        arr = np.array(data)
        weights = np.ones(window) / window
        ma = np.convolve(arr, weights, mode='valid')
        
        # Pad the beginning to match original length
        padding = [None] * (window - 1)
        return padding + ma.tolist()
    
    @staticmethod
    def growth_decomposition(
        snapshots: List[Dict],
        value_key: str
    ) -> Dict[str, Any]:
        """
        Decompose growth into organic vs accelerated.
        
        Args:
            snapshots: Historical data snapshots
            value_key: Key for the value to analyze
            
        Returns:
            Growth decomposition analysis
        """
        if len(snapshots) < 7:
            return {'error': 'Need at least 7 data points'}
        
        df = pd.DataFrame(snapshots)
        values = df[value_key].values
        
        # Calculate daily growth
        daily_growth = np.diff(values)
        
        # Average daily growth
        avg_growth = np.mean(daily_growth)
        
        # Identify acceleration periods
        acceleration = np.diff(daily_growth)  # Second derivative
        
        return {
            'avg_daily_growth': round(float(avg_growth), 2),
            'total_growth': int(values[-1] - values[0]),
            'growth_std': round(float(np.std(daily_growth)), 2),
            'max_single_day_growth': int(np.max(daily_growth)),
            'accelerating': float(np.mean(acceleration)) > 0
        }
    
    @staticmethod
    def forecast_simple(
        data: List[float],
        periods: int = 7
    ) -> List[float]:
        """
        Simple linear forecasting.
        
        Args:
            data: Historical values
            periods: Number of periods to forecast
            
        Returns:
            Forecasted values
        """
        if len(data) < 3:
            return [data[-1]] * periods if data else [0] * periods
        
        x = np.arange(len(data))
        slope, intercept, _, _, _ = stats.linregress(x, data)
        
        future_x = np.arange(len(data), len(data) + periods)
        forecast = slope * future_x + intercept
        
        return [max(0, int(v)) for v in forecast]
    
    @staticmethod
    def seasonality_check(
        data: List[Dict],
        value_key: str,
        date_key: str = 'date'
    ) -> Dict[str, Any]:
        """
        Check for weekly seasonality patterns.
        
        Args:
            data: Data with dates and values
            value_key: Key for the metric value
            date_key: Key for the date
            
        Returns:
            Seasonality analysis
        """
        if len(data) < 14:  # Need at least 2 weeks
            return {'has_seasonality': False, 'reason': 'Insufficient data'}
        
        df = pd.DataFrame(data)
        df[date_key] = pd.to_datetime(df[date_key])
        df['day_of_week'] = df[date_key].dt.dayofweek
        
        # Group by day of week
        daily_avg = df.groupby('day_of_week')[value_key].mean()
        
        # Check variance between days
        cv = daily_avg.std() / daily_avg.mean() if daily_avg.mean() > 0 else 0
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'has_seasonality': cv > 0.1,
            'coefficient_of_variation': round(cv, 3),
            'best_day': days[int(daily_avg.idxmax())],
            'worst_day': days[int(daily_avg.idxmin())],
            'daily_averages': {days[i]: round(v, 2) for i, v in daily_avg.items()}
        }
