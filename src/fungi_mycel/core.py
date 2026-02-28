"""
Core MNIS (Mycelial Network Intelligence Score) computation engine.

The MNIS composite index integrates 8 orthogonal bio-physical indicators
into a single dimensionless score (0-1) representing mycelial network
intelligence and functional state.

MNIS = 0.18·η_NW* + 0.16·E_a* + 0.18·ρ_e* + 0.14·∇C* + 0.12·SER* +
       0.10·K_topo* + 0.07·ABI* + 0.05·BFS*

where Pᵢ* = (Pᵢ_obs - Pᵢ_min) / (Pᵢ_max_ref - Pᵢ_min) normalizes each parameter
to [0, 1] using biome-specific reference distributions.
"""

import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path

# Parameter weights (from Bayesian analysis + Delphi consensus)
MNIS_WEIGHTS = {
    'eta_nw': 0.18,  # Natural Weathering Efficiency
    'e_a': 0.16,     # Adaptive Resilience Index
    'rho_e': 0.18,   # Bioelectrical Pulse Density
    'grad_c': 0.14,  # Chemotropic Navigation Accuracy
    'ser': 0.12,     # Symbiotic Exchange Ratio
    'k_topo': 0.10,  # Topological Expansion Rate
    'abi': 0.07,     # Biodiversity Amplification Index
    'bfs': 0.05,     # Biological Field Stability
}

# Biome-specific reference thresholds
BIOME_REFERENCES = {
    'temperate_broadleaf': {
        'eta_nw': {'min': 0.32, 'max_ref': 0.88},
        'e_a': {'min': 0.30, 'max_ref': 0.80},
        'rho_e': {'min': 0.20, 'max_ref': 0.75},
        'grad_c': {'min': 0.40, 'max_ref': 0.88},
        'ser': {'min': 0.45, 'max_ref': 1.60, 'optimal_min': 0.90, 'optimal_max': 1.10},
        'k_topo': {'min': 1.35, 'max_ref': 1.85},
        'abi': {'min': 1.00, 'max_ref': 2.10},
        'bfs': {'min': 0.28, 'max_ref': 0.85},
    },
    'boreal_conifer': {
        'eta_nw': {'min': 0.28, 'max_ref': 0.82},
        'e_a': {'min': 0.28, 'max_ref': 0.78},
        'rho_e': {'min': 0.18, 'max_ref': 0.72},
        'grad_c': {'min': 0.38, 'max_ref': 0.85},
        'ser': {'min': 0.42, 'max_ref': 1.65, 'optimal_min': 0.88, 'optimal_max': 1.12},
        'k_topo': {'min': 1.30, 'max_ref': 1.80},
        'abi': {'min': 0.95, 'max_ref': 2.00},
        'bfs': {'min': 0.25, 'max_ref': 0.82},
    },
    'tropical_montane': {
        'eta_nw': {'min': 0.35, 'max_ref': 0.90},
        'e_a': {'min': 0.32, 'max_ref': 0.82},
        'rho_e': {'min': 0.22, 'max_ref': 0.78},
        'grad_c': {'min': 0.42, 'max_ref': 0.90},
        'ser': {'min': 0.48, 'max_ref': 1.55, 'optimal_min': 0.92, 'optimal_max': 1.08},
        'k_topo': {'min': 1.40, 'max_ref': 1.88},
        'abi': {'min': 1.10, 'max_ref': 2.20},
        'bfs': {'min': 0.30, 'max_ref': 0.88},
    },
    'mediterranean_woodland': {
        'eta_nw': {'min': 0.30, 'max_ref': 0.85},
        'e_a': {'min': 0.29, 'max_ref': 0.79},
        'rho_e': {'min': 0.19, 'max_ref': 0.73},
        'grad_c': {'min': 0.39, 'max_ref': 0.86},
        'ser': {'min': 0.44, 'max_ref': 1.62, 'optimal_min': 0.89, 'optimal_max': 1.11},
        'k_topo': {'min': 1.33, 'max_ref': 1.82},
        'abi': {'min': 1.02, 'max_ref': 2.05},
        'bfs': {'min': 0.27, 'max_ref': 0.84},
    },
    'subarctic_birch': {
        'eta_nw': {'min': 0.25, 'max_ref': 0.78},
        'e_a': {'min': 0.25, 'max_ref': 0.75},
        'rho_e': {'min': 0.15, 'max_ref': 0.68},
        'grad_c': {'min': 0.35, 'max_ref': 0.82},
        'ser': {'min': 0.40, 'max_ref': 1.70, 'optimal_min': 0.85, 'optimal_max': 1.15},
        'k_topo': {'min': 1.28, 'max_ref': 1.75},
        'abi': {'min': 0.90, 'max_ref': 1.90},
        'bfs': {'min': 0.22, 'max_ref': 0.80},
    },
}

# MNIS classification thresholds
MNIS_CLASSES = {
    'EXCELLENT': (0.00, 0.25),
    'GOOD': (0.25, 0.44),
    'MODERATE': (0.44, 0.62),
    'CRITICAL': (0.62, 0.80),
    'COLLAPSE': (0.80, 1.00),
}


@dataclass
class MNISResult:
    """Container for MNIS computation results."""
    
    mnis_score: float
    class_name: str
    parameters: Dict[str, float]
    normalized_params: Dict[str, float]
    biome: str
    site_id: Optional[str] = None
    mnu_id: Optional[str] = None
    timestamp: Optional[str] = None
    warning_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'mnis_score': self.mnis_score,
            'class': self.class_name,
            'parameters': self.parameters,
            'normalized_params': self.normalized_params,
            'biome': self.biome,
            'site_id': self.site_id,
            'mnu_id': self.mnu_id,
            'timestamp': self.timestamp,
            'warning_flags': self.warning_flags,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class MNIS:
    """
    Mycelial Network Intelligence Score calculator.
    
    This class handles the computation of MNIS from raw parameter values,
    including biome-specific normalization and classification.
    
    Attributes:
        biome: Biome type for reference thresholds
        weights: Parameter weights for composite score
        references: Biome-specific reference thresholds
    """
    
    def __init__(self, biome: str = 'temperate_broadleaf'):
        """
        Initialize MNIS calculator for specific biome.
        
        Args:
            biome: Biome type (temperate_broadleaf, boreal_conifer, 
                   tropical_montane, mediterranean_woodland, subarctic_birch)
        
        Raises:
            ValueError: If biome is not recognized
        """
        if biome not in BIOME_REFERENCES:
            raise ValueError(f"Unknown biome: {biome}. Must be one of {list(BIOME_REFERENCES.keys())}")
        
        self.biome = biome
        self.weights = MNIS_WEIGHTS
        self.references = BIOME_REFERENCES[biome]
    
    def normalize_parameter(self, param_name: str, value: float) -> float:
        """
        Normalize a parameter value to [0, 1] using biome-specific references.
        
        Args:
            param_name: Parameter name (eta_nw, rho_e, etc.)
            value: Raw parameter value
            
        Returns:
            Normalized value in [0, 1]
        
        Raises:
            ValueError: If param_name not found or value out of reasonable range
        """
        if param_name not in self.references:
            raise ValueError(f"Unknown parameter: {param_name}")
        
        ref = self.references[param_name]
        min_val = ref['min']
        max_val = ref['max_ref']
        
        # Special handling for SER (optimal range in middle)
        if param_name == 'ser':
            optimal_min = ref.get('optimal_min', 0.9)
            optimal_max = ref.get('optimal_max', 1.1)
            
            if optimal_min <= value <= optimal_max:
                return 1.0  # Perfect exchange ratio
            elif value < optimal_min:
                # Below optimal: scale from min to optimal_min
                return max(0, (value - min_val) / (optimal_min - min_val))
            else:  # value > optimal_max
                # Above optimal: scale from optimal_max to max_ref
                return max(0, 1 - (value - optimal_max) / (max_val - optimal_max))
        
        # Standard normalization for other parameters
        if value < min_val:
            return 0.0
        elif value > max_val:
            return 1.0
        else:
            return (value - min_val) / (max_val - min_val)
    
    def compute(self, parameters: Dict[str, float]) -> MNISResult:
        """
        Compute MNIS from raw parameter values.
        
        Args:
            parameters: Dictionary with parameter names and raw values
                       Must contain all 8 parameters
        
        Returns:
            MNISResult object with score, class, and normalized values
        
        Raises:
            ValueError: If missing parameters
        """
        # Check for missing parameters
        missing = set(self.weights.keys()) - set(parameters.keys())
        if missing:
            raise ValueError(f"Missing parameters: {missing}")
        
        # Normalize each parameter
        normalized = {}
        warnings = []
        
        for param_name in self.weights.keys():
            raw_value = parameters[param_name]
            norm_value = self.normalize_parameter(param_name, raw_value)
            normalized[param_name] = norm_value
            
            # Check for extreme values
            if norm_value == 0.0:
                warnings.append(f"{param_name} at minimum threshold")
            elif norm_value == 1.0:
                warnings.append(f"{param_name} at maximum threshold")
        
        # Compute weighted sum
        mnis_score = sum(
            self.weights[param] * normalized[param]
            for param in self.weights.keys()
        )
        
        # Determine class
        mnis_class = 'UNKNOWN'
        for class_name, (low, high) in MNIS_CLASSES.items():
            if low <= mnis_score < high:
                mnis_class = class_name
                break
        
        return MNISResult(
            mnis_score=mnis_score,
            class_name=mnis_class,
            parameters=parameters,
            normalized_params=normalized,
            biome=self.biome,
            warning_flags=warnings
        )
    
    def batch_compute(self, parameter_list: List[Dict[str, float]]) -> List[MNISResult]:
        """
        Compute MNIS for multiple samples.
        
        Args:
            parameter_list: List of parameter dictionaries
            
        Returns:
            List of MNISResult objects
        """
        return [self.compute(params) for params in parameter_list]
    
    @staticmethod
    def load_config(config_path: Union[str, Path]) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def compare_results(results: List[MNISResult]) -> Dict:
        """
        Compare multiple MNIS results.
        
        Args:
            results: List of MNISResult objects
            
        Returns:
            Dictionary with comparison statistics
        """
        scores = [r.mnis_score for r in results]
        
        return {
            'mean': np.mean(scores),
            'std': np.std(scores),
            'min': np.min(scores),
            'max': np.max(scores),
            'median': np.median(scores),
            'count': len(scores),
            'class_distribution': {
                cls: sum(1 for r in results if r.class_name == cls)
                for cls in MNIS_CLASSES.keys()
            }
        }


# Convenience function
def compute_mnis(parameters: Dict[str, float], biome: str = 'temperate_broadleaf') -> MNISResult:
    """
    Convenience function to compute MNIS.
    
    Args:
        parameters: Dictionary with parameter values
        biome: Biome type
    
    Returns:
        MNISResult object
    """
    calculator = MNIS(biome=biome)
    return calculator.compute(parameters)
