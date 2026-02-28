"""
BFS - Biological Field Stability

Measures the temporal stability of the mycelial network's functional state -
its capacity to maintain consistent performance across seasonal cycles and
inter-annual climate variability.

Physical mechanism: BFS is computed as the inverse of the coefficient of
variation (CV) of MNIS composite scores across a rolling time window.
High BFS indicates consistent function; declining BFS indicates critical
slowing down and approaching tipping points.

Units: Inverse coefficient of variation (1/CV)
Reference range: 0.28 - 0.85
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass
from scipy import stats


@dataclass
class TimeSeriesPoint:
    """Container for time series data point."""
    
    timestamp: float  # days since start
    mnis_value: float  # MNIS score
    site_id: str
    season: str  # 'spring', 'summer', 'autumn', 'winter'
    confidence: float  # measurement confidence


@dataclass
class BFSResult:
    """Container for BFS calculation results."""
    
    value: float  # BFS = 1/CV
    cv: float  # coefficient of variation
    mean_mnis: float
    std_mnis: float
    n_points: int
    time_span_days: float
    trend_slope: float  # MNIS trend over time
    ar1_coefficient: float  # lag-1 autocorrelation
    stability_class: str  # 'STABLE', 'VARIABLE', 'DECLINING', 'CRITICAL'
    warnings: List[str] = None


class BFSCalculator:
    """
    Calculator for Biological Field Stability (BFS).
    
    BFS = 1 / CV = μ / σ
    
    where:
        μ = mean MNIS over rolling window
        σ = standard deviation of MNIS
        CV = coefficient of variation
    
    For tipping point detection, we also monitor:
        - Increasing variance (critical slowing down)
        - Increasing autocorrelation (AR1)
    """
    
    def __init__(self, window_years: int = 3):
        """
        Initialize BFS calculator.
        
        Args:
            window_years: Rolling window size in years
        """
        self.window_days = window_years * 365
    
    def classify_stability(
        self,
        bfs: float,
        ar1: float,
        trend: float
    ) -> str:
        """
        Classify stability regime.
        """
        if bfs > 0.68 and ar1 < 0.3 and abs(trend) < 0.01:
            return 'STABLE'
        elif bfs > 0.48 and ar1 < 0.5:
            return 'VARIABLE'
        elif bfs > 0.28:
            if ar1 > 0.7 or trend < -0.02:
                return 'CRITICAL'
            else:
                return 'DECLINING'
        else:
            return 'CRITICAL'
    
    def compute_ar1(self, values: List[float]) -> float:
        """Compute lag-1 autocorrelation."""
        if len(values) < 3:
            return 0.0
        
        # Remove trend
        x = np.arange(len(values))
        z = np.polyfit(x, values, 1)
        trend = np.polyval(z, x)
        detrended = values - trend
        
        # Compute AR1
        ar1 = np.corrcoef(detrended[:-1], detrended[1:])[0, 1]
        return max(-1.0, min(1.0, ar1)) if not np.isnan(ar1) else 0.0
    
    def compute_trend(self, values: List[float], times: List[float]) -> float:
        """Compute linear trend (slope) over time."""
        if len(values) < 2:
            return 0.0
        
        # Convert times to years for interpretable slope
        times_years = np.array(times) / 365
        
        slope, _, _, _, _ = stats.linregress(times_years, values)
        return slope
    
    def compute_from_timeseries(
        self,
        mnis_values: List[float],
        timestamps: List[float],
        site_id: Optional[str] = None
    ) -> BFSResult:
        """
        Compute BFS from MNIS time series.
        
        Args:
            mnis_values: List of MNIS scores
            timestamps: List of timestamps (days since start)
            site_id: Site identifier
        
        Returns:
            BFSResult object
        """
        if len(mnis_values) < 4:
            return BFSResult(
                value=0.0,
                cv=0.0,
                mean_mnis=np.mean(mnis_values) if mnis_values else 0,
                std_mnis=np.std(mnis_values) if mnis_values else 0,
                n_points=len(mnis_values),
                time_span_days=max(timestamps) - min(timestamps) if timestamps else 0,
                trend_slope=0.0,
                ar1_coefficient=0.0,
                stability_class='INSUFFICIENT_DATA',
                warnings=["Insufficient data for stability analysis"]
            )
        
        # Calculate basic statistics
        mean_mnis = np.mean(mnis_values)
        std_mnis = np.std(mnis_values)
        
        # Coefficient of variation (handle zero mean)
        if mean_mnis != 0:
            cv = std_mnis / mean_mnis
            bfs = 1.0 / cv if cv > 0 else float('inf')
        else:
            cv = 0
            bfs = 0
        
        # Compute trend
        trend = self.compute_trend(mnis_values, timestamps)
        
        # Compute AR1 for recent data (last 3 years or all if shorter)
        if len(mnis_values) > 10:
            # Use last 10 points for AR1
            ar1 = self.compute_ar1(mnis_values[-10:])
        else:
            ar1 = self.compute_ar1(mnis_values)
        
        # Classify stability
        stability_class = self.classify_stability(bfs, ar1, trend)
        
        # Calculate time span
        time_span = max(timestamps) - min(timestamps)
        
        # Generate warnings
        warnings = []
        if bfs < 0.28:
            warnings.append("Critically low stability - system near collapse")
        elif bfs < 0.48:
            warnings.append("Low stability - increasing variability")
        
        if ar1 > 0.7:
            warnings.append("High autocorrelation - critical slowing down detected")
        
        if trend < -0.05:
            warnings.append(f"Rapid decline ({trend*100:.1f}% per year)")
        elif trend < -0.02:
            warnings.append(f"Moderate decline ({trend*100:.1f}% per year)")
        
        if time_span < 365*2:
            warnings.append("Time series shorter than 2 years - BFS may be unreliable")
        
        # Cap BFS at reasonable values
        bfs = min(2.0, max(0.0, bfs))
        
        return BFSResult(
            value=bfs,
            cv=cv,
            mean_mnis=mean_mnis,
            std_mnis=std_mnis,
            n_points=len(mnis_values),
            time_span_days=time_span,
            trend_slope=trend,
            ar1_coefficient=ar1,
            stability_class=stability_class,
            warnings=warnings
        )
    
    def detect_tipping_point(
        self,
        mnis_values: List[float],
        timestamps: List[float],
        window_size: int = 5
    ) -> Dict[str, float]:
        """
        Detect early warning signals of tipping points.
        
        Returns:
            Dictionary with indicators:
            - variance_ratio: increase in variance
            - ar1_ratio: increase in autocorrelation
            - skewness: change in distribution shape
        """
        if len(mnis_values) < 2 * window_size:
            return {}
        
        # Split into early and late periods
        early = mnis_values[:window_size]
        late = mnis_values[-window_size:]
        
        # Variance ratio
        var_early = np.var(early)
        var_late = np.var(late)
        variance_ratio = var_late / var_early if var_early > 0 else 1.0
        
        # Autocorrelation ratio
        ar1_early = self.compute_ar1(early)
        ar1_late = self.compute_ar1(late)
        ar1_ratio = ar1_late / ar1_early if ar1_early != 0 else 1.0
        
        # Skewness
        skew_early = stats.skew(early)
        skew_late = stats.skew(late)
        
        return {
            'variance_ratio': variance_ratio,
            'ar1_ratio': ar1_ratio,
            'skewness_early': skew_early,
            'skewness_late': skew_late,
            'variance_increasing': variance_ratio > 1.5,
            'ar1_increasing': ar1_ratio > 1.3,
        }
    
    @staticmethod
    def generate_test_timeseries(
        pattern: str = 'stable',
        n_points: int = 20,
        noise: float = 0.05
    ) -> Tuple[List[float], List[float]]:
        """
        Generate test time series data.
        
        Args:
            pattern: 'stable', 'declining', 'critical', 'cyclic'
            n_points: Number of data points
            noise: Noise level
            
        Returns:
            (mnis_values, timestamps)
        """
        timestamps = np.linspace(0, 5*365, n_points)  # 5 years
        
        if pattern == 'stable':
            # Stable around 0.4
            base = 0.4 + np.random.normal(0, noise, n_points)
            
        elif pattern == 'declining':
            # Linear decline
            trend = np.linspace(0, -0.15, n_points)
            base = 0.5 + trend + np.random.normal(0, noise, n_points)
            
        elif pattern == 'critical':
            # Increasing variance (critical slowing down)
            base = np.zeros(n_points)
            variance = np.linspace(noise, noise*3, n_points)
            for i in range(n_points):
                base[i] = 0.4 + np.random.normal(0, variance[i])
            
        elif pattern == 'cyclic':
            # Seasonal cycle
            seasonal = 0.1 * np.sin(2 * np.pi * timestamps / 365)
            base = 0.4 + seasonal + np.random.normal(0, noise, n_points)
            
        else:
            base = np.random.normal(0.4, noise, n_points)
        
        # Ensure values in valid range
        mnis_values = np.clip(base, 0.1, 0.9)
        
        return mnis_values.tolist(), timestamps.tolist()


# Convenience function
def compute_bfs(
    mnis_values: List[float],
    timestamps: List[float],
    **kwargs
) -> float:
    """
    Convenience function to compute BFS.
    
    Args:
        mnis_values: List of MNIS scores
        timestamps: List of timestamps (days)
        **kwargs: Additional parameters for BFSCalculator.compute_from_timeseries()
    
    Returns:
        BFS value
    """
    calculator = BFSCalculator()
    result = calculator.compute_from_timeseries(mnis_values, timestamps, **kwargs)
    return result.value
