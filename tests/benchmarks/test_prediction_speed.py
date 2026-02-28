"""
Benchmark tests for prediction speed and performance.
"""

import pytest
import numpy as np
import time
from fungi_mycel.core import MNIS
from fungi_mycel.parameters import compute_rho_e, compute_k_topo
from fungi_mycel.models.ensemble import AIEnsemble


@pytest.mark.benchmark
class TestPredictionSpeed:
    """Benchmark prediction speeds."""
    
    def test_mnis_computation_speed(self, benchmark, sample_parameters):
        """Benchmark MNIS computation speed."""
        
        def compute_mnis():
            mnis = MNIS()
            return mnis.compute(sample_parameters)
        
        result = benchmark(compute_mnis)
        assert result.mnis_score > 0
    
    def test_batch_processing_speed(self, benchmark):
        """Benchmark batch processing speed."""
        mnis = MNIS()
        
        # Generate batch of parameters
        n_batch = 100
        param_batch = []
        for i in range(n_batch):
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
            param_batch.append(params)
        
        def batch_compute():
            return [mnis.compute(p) for p in param_batch]
        
        results = benchmark(batch_compute)
        assert len(results) == n_batch
    
    def test_rho_e_processing_speed(self, benchmark):
        """Benchmark ρ_e processing speed."""
        from fungi_mycel.parameters.rho_e import RhoECalculator
        
        calculator = RhoECalculator(sampling_rate=1000)
        
        # Generate 1 hour of data at 1000 Hz (3.6M samples)
        data = calculator.simulate_activity(duration=1, pattern='normal')
        
        def compute_rho_e():
            return calculator.compute(data, duration_hours=1)
        
        result = benchmark(compute_rho_e)
        assert 0 <= result.value <= 1
    
    def test_k_topo_processing_speed(self, benchmark):
        """Benchmark K_topo fractal dimension computation."""
        from fungi_mycel.parameters.k_topo import KTopoCalculator
        
        calculator = KTopoCalculator()
        
        # Generate test image (512x512)
        image = calculator.generate_test_pattern('foraging', size=512)
        
        def compute_k_topo():
            return calculator.compute_from_image(image)
        
        result = benchmark(compute_k_topo)
        assert 1.0 <= result.value <= 2.0
    
    def test_ensemble_prediction_speed(self, benchmark):
        """Benchmark ensemble prediction speed."""
        ensemble = AIEnsemble()
        
        # Generate dummy data
        spike_data = np.random.randn(1000, 16)
        parameters = np.random.uniform(0.3, 0.8, 8)
        history = np.random.randn(50, 8)
        
        def predict():
            return ensemble.predict(spike_data, parameters, history)
        
        result = benchmark(predict)
        assert 0 <= result.mnis_prediction <= 1
    
    def test_data_loading_speed(self, benchmark, tmp_path):
        """Benchmark data loading speed."""
        from fungi_mycel.io import load_electrode_data, load_parameters
        
        # Create test files
        electrode_file = tmp_path / "test_electrode.npy"
        data = np.random.randn(100000, 16)
        np.save(electrode_file, data)
        
        param_file = tmp_path / "test_params.json"
        import json
        params = {'eta_nw': 0.72, 'rho_e': 0.68}
        with open(param_file, 'w') as f:
            json.dump(params, f)
        
        def load_all():
            ed, sr = load_electrode_data(electrode_file)
            p = load_parameters(param_file)
            return ed, sr, p
        
        ed, sr, p = benchmark(load_all)
        assert ed.shape[1] == 16
        assert 'eta_nw' in p
