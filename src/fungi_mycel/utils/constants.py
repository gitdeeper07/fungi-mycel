"""
FUNGI-MYCEL Constants Module

Centralized constants used throughout the framework.
"""

from typing import Dict, List, Tuple

# Framework version
VERSION = "1.0.0"
DOI = "10.14293/FUNGI-MYCEL.2026.001"

# Dataset statistics
SITE_COUNT = 39
MNU_COUNT = 2648
BIOME_COUNT = 5
TIME_SPAN_YEARS = 19
VALIDATION_ACCURACY = 91.8  # percent

# Biome types
BIOMES = [
    'temperate_broadleaf',
    'boreal_conifer',
    'tropical_montane',
    'mediterranean_woodland',
    'subarctic_birch',
]

# Parameter names and symbols
PARAMETERS = {
    'eta_nw': 'η_NW',  # Natural Weathering Efficiency
    'rho_e': 'ρ_e',    # Bioelectrical Pulse Density
    'grad_c': '∇C',    # Chemotropic Navigation Accuracy
    'ser': 'SER',      # Symbiotic Exchange Ratio
    'k_topo': 'K_topo', # Topological Expansion Rate
    'e_a': 'E_a',      # Adaptive Resilience Index
    'abi': 'ABI',      # Biodiversity Amplification Index
    'bfs': 'BFS',      # Biological Field Stability
}

# Parameter weights for MNIS
PARAMETER_WEIGHTS = {
    'eta_nw': 0.18,
    'e_a': 0.16,
    'rho_e': 0.18,
    'grad_c': 0.14,
    'ser': 0.12,
    'k_topo': 0.10,
    'abi': 0.07,
    'bfs': 0.05,
}

# Parameter units
PARAMETER_UNITS = {
    'eta_nw': 'μg·μL⁻¹·cm⁻²·day⁻¹',
    'rho_e': 'normalized',
    'grad_c': 'normalized',
    'ser': 'dimensionless',
    'k_topo': 'D_f',
    'e_a': 'dimensionless',
    'abi': 'ratio',
    'bfs': '1/CV',
}

# Parameter reference ranges (min, max_ref)
PARAMETER_RANGES = {
    'eta_nw': (0.25, 0.90),
    'rho_e': (0.15, 0.78),
    'grad_c': (0.35, 0.90),
    'ser': (0.40, 1.70),
    'k_topo': (1.28, 1.88),
    'e_a': (0.25, 0.82),
    'abi': (0.90, 2.20),
    'bfs': (0.22, 0.88),
}

# MNIS classification thresholds
MNIS_CLASSES = {
    'EXCELLENT': (0.00, 0.25),
    'GOOD': (0.25, 0.44),
    'MODERATE': (0.44, 0.62),
    'CRITICAL': (0.62, 0.80),
    'COLLAPSE': (0.80, 1.00),
}

# Key findings
KEY_FINDINGS = {
    'prediction_accuracy': 91.8,
    'stress_detection_rate': 94.3,
    'false_alert_rate': 4.2,
    'early_warning_days': 42,
    'rho_e_ktopo_correlation': 0.917,
    'abi_mean': 1.84,
    'bfs_half_time': 4.1,  # years
}

# File formats
SUPPORTED_FORMATS = {
    'image': ['.tif', '.tiff', '.png', '.jpg', '.jpeg'],
    'tabular': ['.csv', '.tsv', '.xlsx', '.parquet'],
    'sequence': ['.fasta', '.fastq', '.fna'],
    'numpy': ['.npy', '.npz'],
    'hdf5': ['.h5', '.hdf5'],
    'netcdf': ['.nc'],
}

# Default configuration paths
DEFAULT_CONFIG_PATHS = [
    '~/.fungi_mycel/config.yaml',
    '/etc/fungi_mycel/config.yaml',
    './config/fungi_mycel.yaml',
]

# Logging levels
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

# API endpoints
API_ENDPOINTS = {
    'health': '/health',
    'mnis': '/api/v1/mnis',
    'sites': '/api/v1/sites',
    'parameters': '/api/v1/parameters',
    'predict': '/api/v1/predict',
    'alerts': '/api/v1/alerts',
}
