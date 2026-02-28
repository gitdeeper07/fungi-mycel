"""
FUNGI-MYCEL Helper Functions

Utility functions for data processing, validation, and analysis.
"""

import numpy as np
import json
import yaml
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
from datetime import datetime
import warnings


def validate_data(
    data: Dict[str, Any],
    required_keys: List[str],
    types: Optional[Dict[str, type]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate that data contains required keys and correct types.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
        types: Optional dictionary mapping keys to expected types
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Check required keys
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")
    
    # Check types
    if types:
        for key, expected_type in types.items():
            if key in data:
                if not isinstance(data[key], expected_type):
                    errors.append(
                        f"Key '{key}' has type {type(data[key])}, "
                        f"expected {expected_type}"
                    )
    
    return len(errors) == 0, errors


def load_site(site_id: str, data_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load site data by ID.
    
    Args:
        site_id: Site identifier (e.g., 'bialowieza-01')
        data_dir: Data directory (default: ./data)
    
    Returns:
        Site data dictionary
    """
    if data_dir is None:
        data_dir = Path('./data')
    
    site_file = data_dir / 'sites' / f"{site_id}.json"
    
    if not site_file.exists():
        raise FileNotFoundError(f"Site {site_id} not found")
    
    with open(site_file, 'r') as f:
        return json.load(f)


def load_mnu(mnu_id: str, data_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load Mycelial Network Unit data by ID.
    
    Args:
        mnu_id: MNU identifier
        data_dir: Data directory
    
    Returns:
        MNU data dictionary
    """
    if data_dir is None:
        data_dir = Path('./data')
    
    mnu_file = data_dir / 'mnu_dataset' / f"{mnu_id}.json"
    
    if not mnu_file.exists():
        raise FileNotFoundError(f"MNU {mnu_id} not found")
    
    with open(mnu_file, 'r') as f:
        return json.load(f)


def get_biome_reference(biome: str) -> Dict[str, Dict[str, float]]:
    """
    Get reference thresholds for a specific biome.
    
    Args:
        biome: Biome type
    
    Returns:
        Dictionary of parameter references
    """
    # Core references (simplified - full in core.py)
    references = {
        'temperate_broadleaf': {
            'eta_nw': {'min': 0.32, 'max_ref': 0.88},
            'rho_e': {'min': 0.20, 'max_ref': 0.75},
            'k_topo': {'min': 1.35, 'max_ref': 1.85},
        },
        'boreal_conifer': {
            'eta_nw': {'min': 0.28, 'max_ref': 0.82},
            'rho_e': {'min': 0.18, 'max_ref': 0.72},
            'k_topo': {'min': 1.30, 'max_ref': 1.80},
        },
        'tropical_montane': {
            'eta_nw': {'min': 0.35, 'max_ref': 0.90},
            'rho_e': {'min': 0.22, 'max_ref': 0.78},
            'k_topo': {'min': 1.40, 'max_ref': 1.88},
        },
        'mediterranean_woodland': {
            'eta_nw': {'min': 0.30, 'max_ref': 0.85},
            'rho_e': {'min': 0.19, 'max_ref': 0.73},
            'k_topo': {'min': 1.33, 'max_ref': 1.82},
        },
        'subarctic_birch': {
            'eta_nw': {'min': 0.25, 'max_ref': 0.78},
            'rho_e': {'min': 0.15, 'max_ref': 0.68},
            'k_topo': {'min': 1.28, 'max_ref': 1.75},
        },
    }
    
    if biome not in references:
        raise ValueError(f"Unknown biome: {biome}")
    
    return references[biome]


def normalize_parameter(
    value: float,
    min_val: float,
    max_val: float,
    clip: bool = True
) -> float:
    """
    Normalize a parameter value to [0, 1] range.
    
    Args:
        value: Raw parameter value
        min_val: Minimum reference value
        max_val: Maximum reference value
        clip: Whether to clip to [0, 1]
    
    Returns:
        Normalized value
    """
    if max_val <= min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    
    if clip:
        normalized = max(0.0, min(1.0, normalized))
    
    return normalized


def calculate_confidence(
    measurements: List[float],
    method: str = 'std'
) -> float:
    """
    Calculate confidence in measurements.
    
    Args:
        measurements: List of repeated measurements
        method: 'std' (standard deviation) or 'cv' (coefficient of variation)
    
    Returns:
        Confidence score (0-1)
    """
    if not measurements:
        return 0.0
    
    if len(measurements) == 1:
        return 0.7  # Default confidence for single measurement
    
    mean_val = np.mean(measurements)
    std_val = np.std(measurements)
    
    if method == 'std':
        # Lower std = higher confidence
        if mean_val == 0:
            return 0.5
        confidence = 1.0 - (std_val / mean_val)
    else:  # CV method
        if mean_val == 0:
            return 0.5
        cv = std_val / mean_val
        confidence = 1.0 / (1.0 + cv)
    
    return max(0.0, min(1.0, confidence))


def detect_outliers(
    data: List[float],
    method: str = 'iqr',
    threshold: float = 1.5
) -> List[int]:
    """
    Detect outliers in a list of values.
    
    Args:
        data: List of numerical values
        method: 'iqr' (interquartile range) or 'zscore'
        threshold: Outlier threshold
    
    Returns:
        List of outlier indices
    """
    if len(data) < 4:
        return []
    
    data_array = np.array(data)
    
    if method == 'iqr':
        q1 = np.percentile(data_array, 25)
        q3 = np.percentile(data_array, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        outliers = np.where(
            (data_array < lower_bound) | (data_array > upper_bound)
        )[0]
        
    elif method == 'zscore':
        mean_val = np.mean(data_array)
        std_val = np.std(data_array)
        
        if std_val == 0:
            return []
        
        z_scores = np.abs((data_array - mean_val) / std_val)
        outliers = np.where(z_scores > threshold)[0]
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return outliers.tolist()


def interpolate_missing(
    data: List[Optional[float]],
    method: str = 'linear'
) -> List[float]:
    """
    Interpolate missing values in a sequence.
    
    Args:
        data: List with None for missing values
        method: 'linear', 'nearest', 'cubic'
    
    Returns:
        List with interpolated values
    """
    # Find indices with values
    indices = np.array([i for i, x in enumerate(data) if x is not None])
    values = np.array([x for x in data if x is not None])
    
    if len(indices) < 2:
        # Not enough data for interpolation
        return [x if x is not None else 0.0 for x in data]
    
    # Create array of all indices
    all_indices = np.arange(len(data))
    
    # Interpolate
    from scipy import interpolate
    f = interpolate.interp1d(
        indices, values,
        kind=method,
        bounds_error=False,
        fill_value='extrapolate'
    )
    
    interpolated = f(all_indices)
    
    return interpolated.tolist()


def resample_time_series(
    times: List[float],
    values: List[float],
    target_interval: float,
    method: str = 'mean'
) -> Tuple[List[float], List[float]]:
    """
    Resample time series to regular intervals.
    
    Args:
        times: Original timestamps
        values: Original values
        target_interval: Target interval in same units as times
        method: 'mean', 'sum', 'max', 'min'
    
    Returns:
        (resampled_times, resampled_values)
    """
    if len(times) < 2:
        return times, values
    
    times = np.array(times)
    values = np.array(values)
    
    # Create regular time grid
    start_time = np.floor(times[0] / target_interval) * target_interval
    end_time = np.ceil(times[-1] / target_interval) * target_interval
    resampled_times = np.arange(start_time, end_time + target_interval, target_interval)
    
    resampled_values = []
    
    for i in range(len(resampled_times) - 1):
        t_start = resampled_times[i]
        t_end = resampled_times[i + 1]
        
        # Find values in this interval
        mask = (times >= t_start) & (times < t_end)
        interval_values = values[mask]
        
        if len(interval_values) == 0:
            resampled_values.append(np.nan)
        else:
            if method == 'mean':
                resampled_values.append(np.mean(interval_values))
            elif method == 'sum':
                resampled_values.append(np.sum(interval_values))
            elif method == 'max':
                resampled_values.append(np.max(interval_values))
            elif method == 'min':
                resampled_values.append(np.min(interval_values))
            else:
                raise ValueError(f"Unknown method: {method}")
    
    return resampled_times[:-1].tolist(), resampled_values


def calculate_correlation_matrix(
    data: Dict[str, List[float]]
) -> Dict[str, Dict[str, float]]:
    """
    Calculate correlation matrix between multiple parameters.
    
    Args:
        data: Dictionary mapping parameter names to value lists
    
    Returns:
        Correlation matrix as nested dictionary
    """
    param_names = list(data.keys())
    n_params = len(param_names)
    
    # Create data matrix
    matrix = []
    for name in param_names:
        matrix.append(data[name])
    
    matrix = np.array(matrix)
    
    # Calculate correlation matrix
    corr_matrix = np.corrcoef(matrix)
    
    # Convert to dictionary
    result = {}
    for i, name_i in enumerate(param_names):
        result[name_i] = {}
        for j, name_j in enumerate(param_names):
            result[name_i][name_j] = float(corr_matrix[i, j])
    
    return result


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
    
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        if config_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif config_path.suffix == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")


def save_results(
    results: Dict[str, Any],
    output_path: Union[str, Path],
    format: str = 'json'
):
    """
    Save results to file.
    
    Args:
        results: Results dictionary
        output_path: Output file path
        format: 'json' or 'yaml'
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    elif format == 'yaml':
        with open(output_path, 'w') as f:
            yaml.dump(results, f, default_flow_style=False)
    else:
        raise ValueError(f"Unsupported format: {format}")


def timestamp_now() -> str:
    """Get current timestamp as string."""
    return datetime.now().isoformat()


def format_mnis_class(mnis_score: float) -> str:
    """
    Get MNIS class name from score.
    
    Args:
        mnis_score: MNIS score (0-1)
    
    Returns:
        Class name
    """
    from fungi_mycel.utils.constants import MNIS_CLASSES
    
    for class_name, (low, high) in MNIS_CLASSES.items():
        if low <= mnis_score < high:
            return class_name
    
    return 'UNKNOWN'
