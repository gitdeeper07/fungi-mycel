"""
Integration tests for complete processing pipeline.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import json

from fungi_mycel.core import MNIS
from fungi_mycel.parameters import compute_rho_e, compute_eta_nw, compute_k_topo
from fungi_mycel.io import load_electrode_data, export_to_json
from fungi_mycel.visualization import plot_mnis_timeseries


class TestProcessingPipeline:
    """Test complete data processing pipeline."""
    
    @pytest.fixture
    def sample_data_dir(self):
        """Create temporary directory with sample data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample electrode data
            electrode_data = np.random.randn(10000, 16) * 10
            np.save(Path(tmpdir) / 'electrode_data.npy', electrode_data)
            
            # Create sample parameters
            params = {
                'site_id': 'test-site',
                'mnu_id': 'MNU-test-001',
                'parameters': {
                    'eta_nw': 0.72,
                    'rho_e': 0.68,
                    'grad_c': 0.71,
                    'ser': 1.05,
                    'k_topo': 1.72,
                    'e_a': 0.65,
                    'abi': 1.84,
                    'bfs': 0.58,
                }
            }
            with open(Path(tmpdir) / 'parameters.json', 'w') as f:
                json.dump(params, f)
            
            yield Path(tmpdir)
    
    def test_full_pipeline(self, sample_data_dir):
        """Test complete analysis pipeline."""
        # 1. Load electrode data
        electrode_file = sample_data_dir / 'electrode_data.npy'
        data, sr = load_electrode_data(electrode_file)
        assert data.shape[1] == 16
        assert sr > 0
        
        # 2. Compute ρ_e
        rho_e_result = compute_rho_e(data, sampling_rate=sr)
        assert 0 <= rho_e_result <= 1
        
        # 3. Load parameters
        param_file = sample_data_dir / 'parameters.json'
        with open(param_file, 'r') as f:
            params = json.load(f)['parameters']
        
        # 4. Compute MNIS
        mnis = MNIS(biome='temperate_broadleaf')
        result = mnis.compute(params)
        
        assert 0 <= result.mnis_score <= 1
        assert result.class_name in ['EXCELLENT', 'GOOD', 'MODERATE', 'CRITICAL', 'COLLAPSE']
        
        # 5. Export results
        output_file = sample_data_dir / 'results.json'
        export_to_json(result.to_dict(), output_file)
        assert output_file.exists()
        
        # 6. Verify exported results
        with open(output_file, 'r') as f:
            exported = json.load(f)
        assert exported['mnis_score'] == result.mnis_score
    
    def test_site_comparison(self, sample_data_dir):
        """Test comparing multiple sites."""
        sites = ['site1', 'site2', 'site3']
        results = []
        
        mnis = MNIS()
        
        for site in sites:
            # Create different parameter sets
            params = {
                'eta_nw': 0.5 + 0.3 * np.random.random(),
                'rho_e': 0.5 + 0.3 * np.random.random(),
                'grad_c': 0.5 + 0.3 * np.random.random(),
                'ser': 1.0 + 0.2 * np.random.random(),
                'k_topo': 1.6 + 0.2 * np.random.random(),
                'e_a': 0.5 + 0.3 * np.random.random(),
                'abi': 1.5 + 0.4 * np.random.random(),
                'bfs': 0.5 + 0.2 * np.random.random(),
            }
            
            result = mnis.compute(params)
            results.append(result)
        
        # Compare results
        comparison = mnis.compare_results(results)
        assert comparison['count'] == 3
        assert comparison['mean'] > 0
    
    def test_time_series_analysis(self):
        """Test time series analysis."""
        # Generate time series
        n_points = 50
        timestamps = np.linspace(0, 365*3, n_points)
        values = 0.4 + 0.1 * np.sin(np.linspace(0, 4*np.pi, n_points))
        values += 0.05 * np.random.randn(n_points)
        values = np.clip(values, 0.1, 0.9)
        
        # Create plot
        fig = plot_mnis_timeseries(timestamps, values, site_name="Test Site")
        assert fig is not None
    
    def test_error_handling(self):
        """Test error handling in pipeline."""
        mnis = MNIS()
        
        # Test with invalid parameters
        with pytest.raises(ValueError):
            mnis.compute({})
        
        # Test with invalid biome
        with pytest.raises(ValueError):
            MNIS(biome='invalid')
        
        # Test with invalid data type
        with pytest.raises(Exception):
            load_electrode_data('nonexistent_file.npy')
