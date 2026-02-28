"""
Unit tests for core MNIS functionality.
"""

import pytest
import numpy as np
from fungi_mycel.core import MNIS, compute_mnis, MNISResult
from fungi_mycel.utils.constants import PARAMETERS, BIOMES


class TestMNISCore:
    """Tests for MNIS core functionality."""
    
    def test_mnis_initialization(self):
        """Test MNIS class initialization."""
        mnis = MNIS(biome='temperate_broadleaf')
        assert mnis.biome == 'temperate_broadleaf'
        assert len(mnis.weights) == 8
        assert 'eta_nw' in mnis.weights
    
    def test_mnis_invalid_biome(self):
        """Test initialization with invalid biome."""
        with pytest.raises(ValueError):
            MNIS(biome='invalid_biome')
    
    def test_normalize_parameter(self):
        """Test parameter normalization."""
        mnis = MNIS(biome='temperate_broadleaf')
        
        # Test within range
        norm = mnis.normalize_parameter('eta_nw', 0.6)
        assert 0 <= norm <= 1
        
        # Test below minimum
        norm = mnis.normalize_parameter('eta_nw', 0.1)
        assert norm == 0.0
        
        # Test above maximum
        norm = mnis.normalize_parameter('eta_nw', 1.0)
        assert norm == 1.0
    
    def test_normalize_ser(self):
        """Test SER normalization (special case)."""
        mnis = MNIS(biome='temperate_broadleaf')
        
        # Optimal range
        norm = mnis.normalize_parameter('ser', 1.0)
        assert norm == 1.0
        
        # Below optimal
        norm = mnis.normalize_parameter('ser', 0.7)
        assert 0 < norm < 1
        
        # Above optimal
        norm = mnis.normalize_parameter('ser', 1.3)
        assert 0 < norm < 1
    
    def test_compute_mnis(self, sample_parameters):
        """Test MNIS computation."""
        mnis = MNIS(biome='temperate_broadleaf')
        result = mnis.compute(sample_parameters)
        
        assert isinstance(result, MNISResult)
        assert 0 <= result.mnis_score <= 1
        assert result.class_name in ['EXCELLENT', 'GOOD', 'MODERATE', 'CRITICAL', 'COLLAPSE']
        assert len(result.parameters) == 8
        assert len(result.normalized_params) == 8
    
    def test_compute_mnis_missing_parameters(self):
        """Test computation with missing parameters."""
        mnis = MNIS()
        incomplete_params = {'eta_nw': 0.5, 'rho_e': 0.5}
        
        with pytest.raises(ValueError):
            mnis.compute(incomplete_params)
    
    def test_convenience_function(self, sample_parameters):
        """Test convenience compute function."""
        result = compute_mnis(sample_parameters, biome='temperate_broadleaf')
        assert isinstance(result, MNISResult)
        assert result.biome == 'temperate_broadleaf'
    
    def test_batch_compute(self, sample_parameters):
        """Test batch computation."""
        mnis = MNIS()
        param_list = [sample_parameters, sample_parameters]
        results = mnis.batch_compute(param_list)
        
        assert len(results) == 2
        assert all(isinstance(r, MNISResult) for r in results)
    
    def test_result_to_dict(self, sample_parameters):
        """Test MNISResult to_dict method."""
        mnis = MNIS()
        result = mnis.compute(sample_parameters)
        result_dict = result.to_dict()
        
        assert 'mnis_score' in result_dict
        assert 'class' in result_dict
        assert 'parameters' in result_dict
        assert 'biome' in result_dict
    
    def test_compare_results(self, sample_parameters):
        """Test comparison of multiple results."""
        mnis = MNIS()
        results = [
            mnis.compute(sample_parameters),
            mnis.compute(sample_parameters),
        ]
        
        comparison = mnis.compare_results(results)
        assert 'mean' in comparison
        assert 'std' in comparison
        assert 'class_distribution' in comparison
    
    def test_different_biomes(self, sample_parameters):
        """Test MNIS across different biomes."""
        for biome in BIOMES:
            mnis = MNIS(biome=biome)
            result = mnis.compute(sample_parameters)
            assert 0 <= result.mnis_score <= 1
    
    def test_warning_generation(self):
        """Test warning flag generation."""
        mnis = MNIS()
        
        # Parameters at extremes
        extreme_params = {
            'eta_nw': 0.1,  # Below min
            'rho_e': 0.1,   # Below min
            'grad_c': 0.1,
            'ser': 2.0,     # Above max
            'k_topo': 1.0,  # Below min
            'e_a': 0.1,
            'abi': 0.5,
            'bfs': 0.1,
        }
        
        result = mnis.compute(extreme_params)
        assert len(result.warning_flags) > 0
