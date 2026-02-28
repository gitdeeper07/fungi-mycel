"""
E_a - Adaptive Resilience Index

Measures the mycelial network's capacity to maintain growth trajectory and
functional output under environmental stress - the biological analog of
structural engineering's safety factor.

Physical mechanism: Growth rate maintenance and recovery capacity under
standardized stress protocols (metal toxicity + osmotic stress).

Units: Dimensionless ratio (0-1)
Reference range: 0.30 - 0.80
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass


@dataclass
class GrowthMeasurement:
    """Container for growth rate measurements."""
    
    rate: float  # μm/hour
    condition: str  # 'control', 'stressed', 'recovery'
    time_point: float  # hours
    n_tips: int  # number of hyphal tips measured
    std_dev: float  # standard deviation


@dataclass
class EAResult:
    """Container for E_a calculation results."""
    
    value: float  # E_a index
    growth_control: float  # control growth rate
    growth_stressed: float  # stressed growth rate
    growth_recovery: float  # recovery growth rate
    suppression_percent: float  # % suppression under stress
    recovery_time: float  # days to full recovery
    resilience_class: str  # 'RESILIENT', 'MODERATE', 'COMPROMISED'
    n_measurements: int
    warnings: List[str] = None


class EACalculator:
    """
    Calculator for Adaptive Resilience Index (E_a).
    
    E_a = (G_stressed / G_control) · exp(-λ · t_stress)
    
    where:
        G_stressed = growth rate under standardized stress
        G_control = growth rate in control condition
        λ = resilience decay coefficient
        t_stress = duration of stress exposure
    """
    
    def __init__(self):
        """Initialize E_a calculator."""
        pass
    
    def classify_resilience(self, e_a: float) -> str:
        """
        Classify resilience level.
        """
        if e_a >= 0.80:
            return 'RESILIENT'
        elif 0.50 <= e_a < 0.80:
            return 'MODERATE'
        else:
            return 'COMPROMISED'
    
    def compute_resilience_decay(
        self,
        recovery_rates: List[float],
        time_points: List[float]
    ) -> float:
        """
        Compute resilience decay coefficient λ from recovery data.
        """
        if len(recovery_rates) < 2:
            return 0.5  # default
        
        # Normalize rates
        rates = np.array(recovery_rates)
        times = np.array(time_points)
        
        # Fit exponential decay: rate = rate0 * exp(-λ * t)
        log_rates = np.log(rates + 1e-6)
        
        # Linear regression on log-transformed data
        coeffs = np.polyfit(times, log_rates, 1)
        lambda_coeff = -coeffs[0]
        
        return max(0.01, min(2.0, lambda_coeff))
    
    def compute(
        self,
        control_growth: float,  # μm/hour
        stressed_growth: float,  # μm/hour
        stress_duration: float = 48.0,  # hours (standard: 48h)
        recovery_rates: Optional[List[float]] = None,
        recovery_times: Optional[List[float]] = None,
        temperature: float = 15.0,
        n_tips_control: int = 40,
        n_tips_stressed: int = 40
    ) -> EAResult:
        """
        Compute E_a from growth measurements.
        
        Args:
            control_growth: Growth rate in control condition
            stressed_growth: Growth rate under stress
            stress_duration: Duration of stress exposure (hours)
            recovery_rates: Growth rates during recovery
            recovery_times: Time points for recovery measurements
            temperature: Temperature during experiment
            n_tips_control: Number of tips measured in control
            n_tips_stressed: Number of tips measured under stress
        
        Returns:
            EAResult object
        """
        # Calculate suppression
        if control_growth > 0:
            suppression = (1 - stressed_growth / control_growth) * 100
        else:
            suppression = 100
        
        # Calculate resilience decay if recovery data available
        recovery_time = None
        recovery_growth = None
        lambda_coeff = 0.5  # default
        
        if recovery_rates and recovery_times and len(recovery_rates) > 0:
            # Find time to 90% recovery
            target = 0.9 * control_growth
            
            for i, rate in enumerate(recovery_rates):
                if rate >= target:
                    recovery_time = recovery_times[i] / 24  # convert to days
                    recovery_growth = rate
                    break
            
            # Compute decay coefficient
            lambda_coeff = self.compute_resilience_decay(
                recovery_rates, recovery_times
            )
        
        # Calculate E_a
        if control_growth > 0:
            growth_ratio = stressed_growth / control_growth
        else:
            growth_ratio = 0
        
        e_a = growth_ratio * np.exp(-lambda_coeff * stress_duration / 24)
        
        # Apply temperature correction if needed
        if temperature != 15:
            # Optimal temperature ~15°C for most fungi
            temp_factor = np.exp(-0.5 * ((temperature - 15) / 10)**2)
            e_a *= temp_factor
        
        # Clamp to valid range
        e_a = min(1.0, max(0.0, e_a))
        
        # Classify resilience
        resilience_class = self.classify_resilience(e_a)
        
        # Generate warnings
        warnings = []
        if e_a < 0.3:
            warnings.append("Critically low resilience - network severely compromised")
        elif e_a < 0.5:
            warnings.append("Low resilience - recovery may be slow")
        
        if suppression > 70:
            warnings.append(f"Severe growth suppression ({suppression:.1f}%)")
        elif suppression > 50:
            warnings.append(f"Major growth suppression ({suppression:.1f}%)")
        
        if recovery_time and recovery_time > 14:
            warnings.append(f"Slow recovery ({recovery_time:.1f} days)")
        
        # Use recovery growth if available
        if recovery_growth is None:
            recovery_growth = stressed_growth
        
        if recovery_time is None:
            recovery_time = 7.0  # default estimate
        
        return EAResult(
            value=e_a,
            growth_control=control_growth,
            growth_stressed=stressed_growth,
            growth_recovery=recovery_growth,
            suppression_percent=suppression,
            recovery_time=recovery_time,
            resilience_class=resilience_class,
            n_measurements=n_tips_control + n_tips_stressed,
            warnings=warnings
        )
    
    def estimate_from_field_data(
        self,
        ndvi_decline: float,  # NDVI decline during drought (%)
        soil_moisture: float,  # % of field capacity
        fungal_richness: int,  # number of fungal species
        disturbance_severity: float  # 0-1 scale
    ) -> float:
        """
        Estimate E_a from field data when experimental data unavailable.
        """
        # Base resilience from fungal diversity
        base_resilience = min(1.0, fungal_richness / 20)  # 20+ species = high resilience
        
        # Impact of disturbance
        disturbance_impact = 1 - disturbance_severity
        
        # Impact of drought
        drought_impact = 1 - (ndvi_decline / 100) * (1 - soil_moisture / 100)
        
        # Combined estimate
        estimated = base_resilience * disturbance_impact * drought_impact
        
        return min(1.0, max(0.1, estimated))


# Convenience function
def compute_e_a(
    control_growth: float,
    stressed_growth: float,
    **kwargs
) -> float:
    """
    Convenience function to compute E_a.
    
    Args:
        control_growth: Growth rate in control condition
        stressed_growth: Growth rate under stress
        **kwargs: Additional parameters for EACalculator.compute()
    
    Returns:
        E_a value
    """
    calculator = EACalculator()
    result = calculator.compute(control_growth, stressed_growth, **kwargs)
    return result.value
