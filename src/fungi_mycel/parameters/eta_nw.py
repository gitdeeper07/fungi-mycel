"""
η_NW - Natural Weathering Efficiency

Measures the rate at which mycelial network chemically dissolves mineral substrates,
extracting phosphorus, potassium, calcium, and other nutrients.

Physical mechanism: Production of organic acids (oxalic, citric) that attack
mineral surfaces at the nanometer scale.

Units: μg mineral · μL acid⁻¹ · cm⁻² hyphae · day⁻¹
Reference range: 0.48 - 2.3 μg·μL⁻¹·cm⁻²·day⁻¹
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple
from dataclasses import dataclass


@dataclass
class EtaNWResult:
    """Container for η_NW calculation results."""
    
    value: float
    mineral_type: str
    dissolution_rate: float  # μg/day
    acid_production: float   # μL·cm⁻²·day⁻¹
    contact_area: float      # cm²
    confidence: float        # 0-1
    warnings: list = None


class EtaNWCalculator:
    """
    Calculator for Natural Weathering Efficiency (η_NW).
    
    η_NW = (dM/dt) / (V_acid · A_contact · T)
    
    where:
        dM/dt = rate of mineral mass dissolution (μg/day)
        V_acid = volumetric exudate production rate (μL·cm⁻²·day⁻¹)
        A_contact = total hyphal-mineral contact surface area (cm²)
        T = incubation time (days)
    """
    
    def __init__(self, calibration_file: Optional[str] = None):
        """Initialize η_NW calculator."""
        self.calibration_file = calibration_file
        self._load_calibration()
    
    def _load_calibration(self):
        """Load calibration data if available."""
        # Default calibration factors
        self.mineral_factors = {
            'apatite': 1.0,
            'feldspar': 0.85,
            'biotite': 1.2,
            'quartz': 0.3,
            'calcite': 1.5,
            'olivine': 1.1,
        }
    
    def compute(
        self,
        dissolution_rate: float,      # μg/day
        acid_production: float,       # μL·cm⁻²·day⁻¹
        contact_area: float,          # cm²
        incubation_time: float = 1.0, # days
        mineral_type: str = 'apatite',
        temperature: float = 15.0,    # °C
        ph: float = 5.5,
    ) -> EtaNWResult:
        """
        Compute η_NW from measured parameters.
        
        Args:
            dissolution_rate: Rate of mineral mass dissolution (μg/day)
            acid_production: Volumetric exudate production rate (μL·cm⁻²·day⁻¹)
            contact_area: Total hyphal-mineral contact surface area (cm²)
            incubation_time: Duration of incubation (days)
            mineral_type: Type of mineral substrate
            temperature: Soil temperature (°C)
            ph: Soil pH
            
        Returns:
            EtaNWResult object with calculated value and metadata
        """
        # Apply mineral-specific correction
        mineral_factor = self.mineral_factors.get(mineral_type, 1.0)
        
        # Temperature correction (Arrhenius-type)
        temp_factor = np.exp(0.05 * (temperature - 15))
        
        # pH correction (optimal range 4.5-6.5)
        if 4.5 <= ph <= 6.5:
            ph_factor = 1.0
        else:
            ph_factor = max(0.5, 1.0 - 0.2 * abs(ph - 5.5))
        
        # Calculate η_NW
        base_value = dissolution_rate / (acid_production * contact_area * incubation_time)
        eta_nw = base_value * mineral_factor * temp_factor * ph_factor
        
        # Calculate confidence based on measurement quality
        confidence = self._calculate_confidence(
            dissolution_rate, acid_production, contact_area
        )
        
        # Generate warnings if needed
        warnings = []
        if eta_nw < 0.3:
            warnings.append("Very low weathering efficiency")
        elif eta_nw > 2.5:
            warnings.append("Exceptionally high weathering rate - verify measurements")
        
        if ph < 4.0:
            warnings.append("Extreme acidity - may inhibit fungal activity")
        elif ph > 7.5:
            warnings.append("Alkaline conditions - suboptimal for weathering")
        
        return EtaNWResult(
            value=eta_nw,
            mineral_type=mineral_type,
            dissolution_rate=dissolution_rate,
            acid_production=acid_production,
            contact_area=contact_area,
            confidence=confidence,
            warnings=warnings
        )
    
    def _calculate_confidence(
        self,
        dissolution_rate: float,
        acid_production: float,
        contact_area: float
    ) -> float:
        """Calculate confidence in measurement."""
        # Simplified confidence calculation
        # In practice, this would use measurement uncertainties
        
        if all(v > 0 for v in [dissolution_rate, acid_production, contact_area]):
            return 0.95
        else:
            return 0.7
    
    @staticmethod
    def estimate_from_soil_chemistry(
        phosphorus: float,        # μg P/g soil
        calcium: float,           # μg Ca/g soil
        organic_matter: float,    # %
        fungal_biomass: float,    # μg C/g soil
    ) -> float:
        """
        Estimate η_NW from soil chemistry when direct measurements unavailable.
        
        This is a simplified estimation for preliminary assessments.
        """
        # Empirical formula based on soil properties
        base_rate = 0.5
        
        # Phosphorus limitation increases weathering
        p_factor = np.exp(-phosphorus / 100) if phosphorus > 0 else 2.0
        
        # Organic matter supports fungal activity
        om_factor = 1.0 + 0.1 * organic_matter
        
        # Fungal biomass directly related to weathering
        biomass_factor = fungal_biomass / 100 if fungal_biomass > 0 else 1.0
        
        estimated = base_rate * p_factor * om_factor * biomass_factor
        
        return min(max(estimated, 0.3), 2.5)


# Convenience function
def compute_eta_nw(
    dissolution_rate: float,
    acid_production: float,
    contact_area: float,
    **kwargs
) -> float:
    """
    Convenience function to compute η_NW.
    
    Args:
        dissolution_rate: Rate of mineral mass dissolution (μg/day)
        acid_production: Volumetric exudate production rate (μL·cm⁻²·day⁻¹)
        contact_area: Total hyphal-mineral contact surface area (cm²)
        **kwargs: Additional parameters for EtaNWCalculator.compute()
    
    Returns:
        η_NW value
    """
    calculator = EtaNWCalculator()
    result = calculator.compute(
        dissolution_rate=dissolution_rate,
        acid_production=acid_production,
        contact_area=contact_area,
        **kwargs
    )
    return result.value
