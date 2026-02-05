"""Prediction Models using Prophet for Content Analytics Tool."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class GrowthPredictor:
    """Time series forecasting for social media metrics using Prophet."""
    
    def __init__(self):
        """Initialize the growth predictor."""
        try:
            from prophet import Prophet
            self._Prophet = Prophet
            self._available = True
        except ImportError:
            self._available = False
            self._Prophet = None
    
    def is_available(self) -> bool:
        """Check if Prophet is available.
        
        Returns:
            True if Prophet is installed and available
        """
        return self._available
    
    def prepare_data(
        self,
        snapshots: List[Any],
        date_field: str = 'snapshot_date',
        value_field: str = 'subscriber_count'
    ) -> pd.DataFrame:
        """Prepare data for Prophet model.
        
        Args:
            snapshots: List of snapshot objects or dictionaries
            date_field: Name of the date field
            value_field: Name of the value field to forecast
            
        Returns:
            DataFrame with 'ds' (date) and 'y' (value) columns
        """
        data = []
        
        for snapshot in snapshots:
            if hasattr(snapshot, date_field):
                date_val = getattr(snapshot, date_field)
                value_val = getattr(snapshot, value_field, 0)
            else:
                date_val = snapshot.get(date_field)
                value_val = snapshot.get(value_field, 0)
            
            if date_val:
                data.append({
                    'ds': pd.to_datetime(date_val),
                    'y': float(value_val)
                })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('ds').drop_duplicates(subset='ds')
        
        return df
    
    def forecast(
        self,
        snapshots: List[Any],
        periods: int = 30,
        date_field: str = 'snapshot_date',
        value_field: str = 'subscriber_count'
    ) -> Optional[Dict[str, Any]]:
        """Generate forecast using Prophet.
        
        Args:
            snapshots: List of historical snapshots
            periods: Number of days to forecast
            date_field: Name of the date field in snapshots
            value_field: Name of the value field to forecast
            
        Returns:
            Dictionary with forecast data and metrics, or None if unavailable
        """
        if not self._available:
            return self._fallback_forecast(snapshots, periods, date_field, value_field)
        
        df = self.prepare_data(snapshots, date_field, value_field)
        
        if len(df) < 2:
            return None
        
        try:
            # Initialize and fit Prophet model
            model = self._Prophet(
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            # Extract relevant data
            return {
                'historical': df.to_dict('records'),
                'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).to_dict('records'),
                'metrics': {
                    'last_value': float(df['y'].iloc[-1]) if not df.empty else 0,
                    'predicted_value': float(forecast['yhat'].iloc[-1]),
                    'growth_rate': self._calculate_growth_rate(
                        float(df['y'].iloc[-1]) if not df.empty else 0,
                        float(forecast['yhat'].iloc[-1])
                    )
                }
            }
        except Exception as e:
            print(f"Prophet forecasting error: {e}")
            return self._fallback_forecast(snapshots, periods, date_field, value_field)
    
    def _fallback_forecast(
        self,
        snapshots: List[Any],
        periods: int,
        date_field: str,
        value_field: str
    ) -> Optional[Dict[str, Any]]:
        """Simple linear forecast as fallback when Prophet is unavailable.
        
        Args:
            snapshots: List of historical snapshots
            periods: Number of days to forecast
            date_field: Name of the date field
            value_field: Name of the value field
            
        Returns:
            Dictionary with forecast data
        """
        df = self.prepare_data(snapshots, date_field, value_field)
        
        if len(df) < 2:
            return None
        
        # Simple linear regression
        x = np.arange(len(df))
        y = df['y'].values
        
        # Calculate slope and intercept
        slope = np.polyfit(x, y, 1)[0]
        last_value = y[-1]
        
        # Generate forecast
        forecast_dates = pd.date_range(
            start=df['ds'].iloc[-1] + timedelta(days=1),
            periods=periods
        )
        
        forecast_values = [last_value + slope * (i + 1) for i in range(periods)]
        
        return {
            'historical': df.to_dict('records'),
            'forecast': [
                {
                    'ds': date,
                    'yhat': value,
                    'yhat_lower': value * 0.9,
                    'yhat_upper': value * 1.1
                }
                for date, value in zip(forecast_dates, forecast_values)
            ],
            'metrics': {
                'last_value': float(last_value),
                'predicted_value': float(forecast_values[-1]) if forecast_values else float(last_value),
                'growth_rate': self._calculate_growth_rate(
                    float(last_value),
                    float(forecast_values[-1]) if forecast_values else float(last_value)
                )
            }
        }
    
    def _calculate_growth_rate(self, start: float, end: float) -> float:
        """Calculate growth rate between two values.
        
        Args:
            start: Starting value
            end: Ending value
            
        Returns:
            Growth rate as percentage
        """
        if start == 0:
            return 100.0 if end > 0 else 0.0
        
        return round(((end - start) / start) * 100, 2)
    
    def predict_milestone(
        self,
        snapshots: List[Any],
        target_value: int,
        date_field: str = 'snapshot_date',
        value_field: str = 'subscriber_count',
        max_days: int = 365
    ) -> Optional[datetime]:
        """Predict when a target milestone will be reached.
        
        Args:
            snapshots: List of historical snapshots
            target_value: Target value to reach
            date_field: Name of the date field
            value_field: Name of the value field
            max_days: Maximum days to forecast
            
        Returns:
            Predicted date or None if not reachable within max_days
        """
        forecast_result = self.forecast(snapshots, max_days, date_field, value_field)
        
        if not forecast_result:
            return None
        
        for point in forecast_result['forecast']:
            if point['yhat'] >= target_value:
                return pd.to_datetime(point['ds']).to_pydatetime()
        
        return None
