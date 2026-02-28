"""
FUNGI-MYCEL: Mycelial Network Intelligence Framework
=====================================================

A quantitative framework for decoding mycelial network intelligence,
bioelectrical communication, and sub-surface ecological sovereignty.

The framework introduces the Mycelial Network Intelligence Score (MNIS),
an 8-parameter composite index validated across 39 sites and 5 biomes.

Key Components:
    - parameters: Individual parameter calculators (η_NW, ρ_e, ∇C, SER, K_topo, E_a, ABI, BFS)
    - analysis: Core analysis and MNIS computation
    - models: AI ensemble (CNN + XGBoost + LSTM)
    - utils: Utility functions and helpers
    - io: Data input/output handlers
    - visualization: Plotting and dashboard components
    - cli: Command-line interface

Version: 1.0.0
Author: Samir Baladi <gitdeeper@gmail.com>
DOI: 10.14293/FUNGI-MYCEL.2026.001
"""

__version__ = "1.0.0"
__author__ = "Samir Baladi"
__email__ = "gitdeeper@gmail.com"
__doi__ = "10.14293/FUNGI-MYCEL.2026.001"

# Import main components
from fungi_mycel.core import MNIS, compute_mnis
from fungi_mycel.parameters import (
    eta_nw,      # Natural Weathering Efficiency
    rho_e,       # Bioelectrical Pulse Density
    grad_c,      # Chemotropic Navigation
    ser,         # Symbiotic Exchange Ratio
    k_topo,      # Topological Expansion
    e_a,         # Adaptive Resilience
    abi,         # Biodiversity Amplification
    bfs          # Biological Field Stability
)
from fungi_mycel.models import AIEnsemble
from fungi_mycel.utils import validate_data, load_site

__all__ = [
    'MNIS',
    'compute_mnis',
    'eta_nw',
    'rho_e',
    'grad_c',
    'ser',
    'k_topo',
    'e_a',
    'abi',
    'bfs',
    'AIEnsemble',
    'validate_data',
    'load_site',
]
