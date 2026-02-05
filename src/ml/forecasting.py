"""
Content Analytics Platform - Time Series Forecasting
====================================================
Prophet-based forecasting for subscriber and view predictions.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np
from loguru import logger

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not available, using fallback forecasting")


class GrowthForecaster:
    """
    Time series forecasting for social media metrics.
    
    Uses Facebook Prophet for accurate forecasting with:
    - Daily and weekly seasonality
    - Holiday effects
    - Trend changepoint detection
    """
    
    def __init__(self):
        """Initialize forecaster."""
        self.models = {}
        self.forecast_periods = int(os.getenv('FORECAST_PERIODS', 30))
    
    def forecast_subscribers(
        self,
        historical_data: List[Dict],
        periods: int = None
    ) -> Dict[str, Any]:
        """
        Forecast subscriber growth.
        
        Args:
            historical_data: List of {'date': datetime, 'subscribers': int}
            periods: Days to forecast
            
        Returns:
            Forecast results
        """
        periods = periods or self.forecast_periods
        
        if len(historical_data) < 14:
            return self._fallback_forecast(historical_data, 'subscribers', periods)
        
        if not PROPHET_AVAILABLE:
            return self._fallback_forecast(historical_data, 'subscribers', periods)
        
        return self._prophet_forecast(historical_data, 'subscribers', periods)
    
    def forecast_views(
        self,
        historical_data: List[Dict],
        periods: int = None
    ) -> Dict[str, Any]:
        """
        Forecast total views growth.
        
        Args:
            historical_data: List of {'date': datetime, 'views': int}
            periods: Days to forecast
            
        Returns:
            Forecast results
        """
        periods = periods or self.forecast_periods
        
        if len(historical_data) < 14:
            return self._fallback_forecast(historical_data, 'views', periods)
        
        if not PROPHET_AVAILABLE:
            return self._fallback_forecast(historical_data, 'views', periods)
        
        return self._prophet_forecast(historical_data, 'views', periods)
    
    def _prophet_forecast(
        self,
        data: List[Dict],
        metric: str,
        periods: int
    ) -> Dict[str, Any]:
        """Use Prophet for forecasting."""
        # Prepare data for Prophet
        df = pd.DataFrame(data)
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df[metric]
        df = df[['ds', 'y']].dropna()
        
        if len(df) < 7:
            return self._fallback_forecast(data, metric, periods)
        
        try:
            # Configure Prophet
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=len(df) > 365,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10
            )
            
            # Suppress Prophet logs
            import logging
            logging.getLogger('prophet').setLevel(logging.WARNING)
            
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            # Extract forecast for future dates only
            future_forecast = forecast[forecast['ds'] > df['ds'].max()]
            
            results = {
                'metric': metric,
                'model': 'prophet',
                'periods': periods,
                'last_known_value': int(df['y'].iloc[-1]),
                'forecast': [],
                'summary': {}
            }
            
            for _, row in future_forecast.iterrows():
                results['forecast'].append({
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted': max(0, int(row['yhat'])),
                    'lower_bound': max(0, int(row['yhat_lower'])),
                    'upper_bound': max(0, int(row['yhat_upper']))
                })
            
            if len(results['forecast']) > 0:
                final_forecast = results['forecast'][-1]
                results['summary'] = {
                    'predicted_7d': results['forecast'][6]['predicted'] if len(results['forecast']) > 6 else None,
                    'predicted_30d': final_forecast['predicted'] if periods >= 30 else None,
                    'growth_30d': final_forecast['predicted'] - results['last_known_value'],
                    'growth_rate_30d': round(
                        (final_forecast['predicted'] - results['last_known_value']) 
                        / max(results['last_known_value'], 1) * 100, 2
                    )
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Prophet forecast failed: {e}")
            return self._fallback_forecast(data, metric, periods)
    
    def _fallback_forecast(
        self,
        data: List[Dict],
        metric: str,
        periods: int
    ) -> Dict[str, Any]:
        """Simple linear regression fallback."""
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        values = df[metric].values
        if len(values) < 2:
            return {
                'metric': metric,
                'model': 'fallback',
                'error': 'Insufficient data',
                'forecast': []
            }
        
        # Calculate average daily growth
        daily_growth = np.mean(np.diff(values))
        last_value = values[-1]
        last_date = df['date'].iloc[-1]
        
        forecast = []
        for i in range(1, periods + 1):
            forecast_date = last_date + timedelta(days=i)
            predicted = max(0, int(last_value + daily_growth * i))
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted': predicted,
                'lower_bound': max(0, int(predicted * 0.9)),
                'upper_bound': int(predicted * 1.1)
            })
        
        return {
            'metric': metric,
            'model': 'linear_fallback',
            'periods': periods,
            'last_known_value': int(last_value),
            'avg_daily_growth': round(daily_growth, 2),
            'forecast': forecast,
            'summary': {
                'predicted_7d': forecast[6]['predicted'] if len(forecast) > 6 else None,
                'predicted_30d': forecast[-1]['predicted'] if periods >= 30 else None,
                'growth_30d': forecast[-1]['predicted'] - int(last_value),
                'growth_rate_30d': round(
                    (forecast[-1]['predicted'] - int(last_value)) / max(int(last_value), 1) * 100, 2
                )
            }
        }
    
    def forecast_engagement(
        self,
        posts_data: List[Dict],
        periods: int = 7
    ) -> Dict[str, Any]:
        """
        Forecast expected engagement for future posts.
        
        Args:
            posts_data: Historical posts with engagement
            periods: Number of future posts to forecast
            
        Returns:
            Engagement forecast
        """
        if not posts_data:
            return {'error': 'No data provided'}
        
        df = pd.DataFrame(posts_data)
        
        # Calculate average engagement metrics
        avg_likes = df['like_count'].mean() if 'like_count' in df else 0
        avg_comments = df['comments_count'].mean() if 'comments_count' in df else 0
        avg_engagement_rate = df['engagement_rate'].mean() if 'engagement_rate' in df else 0
        
        # Calculate trend
        if len(df) >= 5:
            recent_avg = df.tail(5)['engagement_rate'].mean() if 'engagement_rate' in df else 0
            trend = 'improving' if recent_avg > avg_engagement_rate else 'declining'
        else:
            trend = 'stable'
        
        return {
            'forecast_periods': periods,
            'expected_likes': round(avg_likes, 0),
            'expected_comments': round(avg_comments, 0),
            'expected_engagement_rate': round(avg_engagement_rate, 4),
            'trend': trend,
            'confidence': 'medium',
            'note': 'Based on historical average performance'
        }
