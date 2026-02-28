"""
Pytest configuration and fixtures for FUNGI-MYCEL tests.
"""

import pytest
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_electrode_data():
    """Generate sample electrode data for testing."""
    np.random.seed(42)
    n_samples = 10000
    n_electrodes = 16
    data = np.random.randn(n_samples, n_electrodes) * 10
    return data


@pytest.fixture
def sample_parameters():
    """Generate sample parameter values."""
    return {
        'eta_nw': 0.72,
        'rho_e': 0.68,
        'grad_c': 0.71,
        'ser': 1.05,
        'k_topo': 1.72,
        'e_a': 0.65,
        'abi': 1.84,
        'bfs': 0.58,
    }


@pytest.fixture
def sample_site_data():
    """Generate sample site metadata."""
    return {
        'site_id': 'test-site-01',
        'name': 'Test Site',
        'biome': 'temperate_broadleaf',
        'country': 'Testland',
        'established': 2020,
        'mnus': 50,
    }


@pytest.fixture
def sample_timeseries():
    """Generate sample time series data."""
    np.random.seed(42)
    n_points = 50
    timestamps = np.linspace(0, 365*3, n_points)
    values = 0.4 + 0.1 * np.sin(np.linspace(0, 4*np.pi, n_points)) + 0.05 * np.random.randn(n_points)
    values = np.clip(values, 0.1, 0.9)
    return timestamps.tolist(), values.tolist()


@pytest.fixture
def sample_binary_image():
    """Generate sample binary image of network."""
    np.random.seed(42)
    size = 256
    image = np.random.random((size, size)) > 0.9
    # Add some structure
    for i in range(0, size, 20):
        image[i:i+5, :] = True
        image[:, i:i+5] = True
    return image


@pytest.fixture
def sample_icpms_data():
    """Generate sample ICP-MS data."""
    return {
        'P': 45.6,
        'K': 120.3,
        'Ca': 78.9,
        'Mg': 34.2,
        'Fe': 12.5,
        'Al': 8.7,
        'Si': 156.4,
    }
