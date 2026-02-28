"""
SER - Symbiotic Exchange Ratio

Measures the stoichiometric balance of the mycorrhizal mutualism - the 'terms of trade'
in the below-ground economy that sustains both fungal and plant partners.

Physical mechanism: Carbon-phosphorus exchange between host plant and fungal network,
measured through isotope tracing (¹³C and ³¹P).

Units: Ratio (dimensionless, relative to Johnson-Graham equilibrium = 1.0)
Reference range: 0.75 - 1.25 (balanced), >1.35 parasitic, <0.75 plant-dominant
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass


@dataclass
class FluxMeasurement:
    """Container for flux measurements."""
    
    carbon_to_fungi: float  # μg C · g root⁻¹ · day⁻¹
    phosphorus_to_plant: float  # μg P · g root⁻¹ · day⁻¹
    carbon_method: str  # '¹³C_pulse', '¹³C_continuous'
    phosphorus_method: str  # '³¹P_dilution', '³²P_tracer'
    timestamp: float  # seconds since start
    confidence: float  # 0-1


@dataclass
class SERResult:
    """Container for SER calculation results."""
    
    value: float  # SER value
    exchange_type: str  # 'balanced', 'parasitic', 'plant_dominant', 'stressed'
    carbon_flux: float
    phosphorus_flux: float
    c_p_ratio: float  # C:P ratio in exchange
    optimal_ratio: float  # biome-specific optimal
    deviation_percent: float  # deviation from optimal
    n_measurements: int
    warnings: List[str] = None


class SERCalculator:
    """
    Calculator for Symbiotic Exchange Ratio (SER).
    
    SER = (Φ_C→fungi / Φ_P→plant) · (1 / Ψ_biocompat)
    
    where:
        Φ_C→fungi = carbon flux from plant to fungal network
        Φ_P→plant = phosphorus flux from fungal network to plant
        Ψ_biocompat = biome-specific compatibility coefficient
    """
    
    def __init__(self, biome: str = 'temperate_broadleaf'):
        """
        Initialize SER calculator.
        
        Args:
            biome: Biome type for optimal stoichiometry
        """
        self.biome = biome
        
        # Biome-specific optimal C:P exchange ratios
        # Based on Johnson-Graham equilibrium model
        self.optimal_ratios = {
            'temperate_broadleaf': 0.85,
            'boreal_conifer': 0.90,
            'tropical_montane': 0.80,
            'mediterranean_woodland': 0.88,
            'subarctic_birch': 0.95,
        }
        
        # Compatibility coefficients
        self.compatibility = {
            'temperate_broadleaf': 1.05,
            'boreal_conifer': 1.10,
            'tropical_montane': 0.95,
            'mediterranean_woodland': 1.02,
            'subarctic_birch': 1.15,
        }
    
    def classify_exchange(self, ser_value: float) -> str:
        """
        Classify the type of symbiotic exchange.
        
        Returns:
            'balanced', 'parasitic', 'plant_dominant', 'stressed'
        """
        if 0.9 <= ser_value <= 1.1:
            return 'balanced'
        elif 1.1 < ser_value <= 1.35:
            return 'stressed'
        elif ser_value > 1.35:
            return 'parasitic'
        elif 0.75 <= ser_value < 0.9:
            return 'stressed'
        else:
            return 'plant_dominant'
    
    def compute(
        self,
        carbon_flux: float,  # μg C · g root⁻¹ · day⁻¹
        phosphorus_flux: float,  # μg P · g root⁻¹ · day⁻¹
        plant_species: Optional[str] = None,
        fungal_species: Optional[str] = None,
        temperature: float = 15.0,
        measurements: Optional[List[FluxMeasurement]] = None
    ) -> SERResult:
        """
        Compute SER from flux measurements.
        
        Args:
            carbon_flux: Carbon flux from plant to fungus
            phosphorus_flux: Phosphorus flux from fungus to plant
            plant_species: Host plant species
            fungal_species: Fungal species
            temperature: Soil temperature (°C)
            measurements: Optional list of multiple measurements
        
        Returns:
            SERResult object with calculated value and metadata
        """
        # Get optimal ratio for biome
        optimal = self.optimal_ratios.get(self.biome, 0.85)
        
        # Get compatibility coefficient
        psi = self.compatibility.get(self.biome, 1.0)
        
        # Temperature correction (Q10 ≈ 2)
        temp_factor = 2.0 ** ((temperature - 15) / 10)
        
        # Calculate raw C:P ratio
        if phosphorus_flux > 0:
            cp_ratio = carbon_flux / phosphorus_flux
        else:
            cp_ratio = float('inf')
            return SERResult(
                value=2.0,  # Maximum SER
                exchange_type='parasitic',
                carbon_flux=carbon_flux,
                phosphorus_flux=phosphorus_flux,
                c_p_ratio=cp_ratio,
                optimal_ratio=optimal,
                deviation_percent=100,
                n_measurements=len(measurements) if measurements else 1,
                warnings=["Zero phosphorus flux - network collapse"]
            )
        
        # Calculate SER
        ser_value = (cp_ratio / optimal) * temp_factor / psi
        
        # Calculate deviation from optimal
        deviation = abs(ser_value - 1.0) * 100
        
        # Classify exchange type
        exchange_type = self.classify_exchange(ser_value)
        
        # Generate warnings
        warnings = []
        if ser_value > 1.35:
            warnings.append(f"Parasitic exchange (SER={ser_value:.2f}) - fungus extracting excess carbon")
        elif ser_value < 0.75:
            warnings.append(f"Plant-dominant exchange (SER={ser_value:.2f}) - nutrient delivery suppressed")
        elif ser_value > 1.1:
            warnings.append(f"Elevated SER - possible nitrogen saturation")
        elif ser_value < 0.9:
            warnings.append(f"Reduced SER - possible fungal stress")
        
        if deviation > 50:
            warnings.append(f"Extreme deviation ({deviation:.1f}%) from optimal stoichiometry")
        
        # Use multiple measurements if available
        n_meas = 1
        if measurements and len(measurements) > 1:
            n_meas = len(measurements)
            # Average would be done here in real implementation
        
        return SERResult(
            value=ser_value,
            exchange_type=exchange_type,
            carbon_flux=carbon_flux,
            phosphorus_flux=phosphorus_flux,
            c_p_ratio=cp_ratio,
            optimal_ratio=optimal,
            deviation_percent=deviation,
            n_measurements=n_meas,
            warnings=warnings
        )
    
    def estimate_from_biomass(
        self,
        fungal_biomass: float,  # g C · m⁻²
        plant_biomass: float,  # g C · m⁻²
        soil_phosphorus: float,  # μg P · g⁻¹
        n_stress: float = 0.5  # nitrogen stress index (0-1)
    ) -> float:
        """
        Estimate SER from biomass and soil data when direct flux unavailable.
        
        This is a simplified estimation for preliminary assessments.
        """
        # Fungal:plant biomass ratio
        fp_ratio = fungal_biomass / max(plant_biomass, 1)
        
        # Phosphorus availability factor
        p_factor = np.exp(-soil_phosphorus / 100)  # P limitation increases SER
        
        # Base SER estimation
        estimated = 1.0 + 0.5 * (fp_ratio - 0.2) + 0.3 * (p_factor - 1) + 0.2 * n_stress
        
        return min(2.0, max(0.5, estimated))
    
    @staticmethod
    def optimal_stoichiometry(
        plant_type: str = 'tree',
        fungal_type: str = 'ectomycorrhizal'
    ) -> Dict[str, float]:
        """
        Get optimal C:P exchange ratios for different plant-fungal pairs.
        """
        optima = {
            ('tree', 'ectomycorrhizal'): 0.85,
            ('tree', 'arbuscular'): 0.75,
            ('shrub', 'ectomycorrhizal'): 0.90,
            ('shrub', 'arbuscular'): 0.80,
            ('grass', 'arbuscular'): 0.70,
        }
        
        return {
            'c_p_ratio': optima.get((plant_type, fungal_type), 0.85),
            'c_flux_range': (50, 200),  # μg C · g⁻¹ · day⁻¹
            'p_flux_range': (5, 30),  # μg P · g⁻¹ · day⁻¹
        }


# Convenience function
def compute_ser(
    carbon_flux: float,
    phosphorus_flux: float,
    biome: str = 'temperate_broadleaf',
    **kwargs
) -> float:
    """
    Convenience function to compute SER.
    
    Args:
        carbon_flux: Carbon flux from plant to fungus
        phosphorus_flux: Phosphorus flux from fungus to plant
        biome: Biome type
        **kwargs: Additional parameters for SERCalculator.compute()
    
    Returns:
        SER value
    """
    calculator = SERCalculator(biome=biome)
    result = calculator.compute(carbon_flux, phosphorus_flux, **kwargs)
    return result.value
