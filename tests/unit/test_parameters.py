"""
Unit tests for parameter modules.
"""

import pytest
import numpy as np
from fungi_mycel.parameters import (
    compute_eta_nw, compute_rho_e, compute_grad_c,
    compute_ser, compute_k_topo, compute_e_a,
    compute_abi, compute_bfs
)
from fungi_mycel.parameters.eta_nw import EtaNWCalculator, EtaNWResult
from fungi_mycel.parameters.rho_e import RhoECalculator, RhoEResult


class TestEtaNW:
    """Tests for η_NW - Natural Weathering Efficiency."""
    
    def test_compute_eta_nw_basic(self):
        """Test basic η_NW computation."""
        result = compute_eta_nw(
            dissolution_rate=50.0,
            acid_production=2.0,
            contact_area=10.0,
            incubation_time=7.0
        )
        assert isinstance(result, float)
        assert 0 < result < 3
    
    def test_eta_nw_calculator(self):
        """Test EtaNWCalculator class."""
        calculator = EtaNWCalculator()
        result = calculator.compute(
            dissolution_rate=50.0,
            acid_production=2.0,
            contact_area=10.0,
            incubation_time=7.0
        )
        assert isinstance(result, EtaNWResult)
        assert hasattr(result, 'value')
        assert hasattr(result, 'mineral_type')
        assert hasattr(result, 'confidence')
    
    def test_eta_nw_mineral_types(self):
        """Test different mineral types."""
        calculator = EtaNWCalculator()
        result1 = calculator.compute(
            dissolution_rate=50.0,
            acid_production=2.0,
            contact_area=10.0,
            mineral_type='apatite'
        )
        result2 = calculator.compute(
            dissolution_rate=50.0,
            acid_production=2.0,
            contact_area=10.0,
            mineral_type='quartz'
        )
        assert result1.value != result2.value
    
    def test_eta_nw_estimate(self):
        """Test estimation from soil chemistry."""
        estimated = EtaNWCalculator.estimate_from_soil_chemistry(
            phosphorus=50,
            calcium=100,
            organic_matter=5,
            fungal_biomass=150
        )
        assert 0.3 <= estimated <= 2.5


class TestRhoE:
    """Tests for ρ_e - Bioelectrical Pulse Density."""
    
    def test_compute_rho_e_basic(self, sample_electrode_data):
        """Test basic ρ_e computation."""
        result = compute_rho_e(sample_electrode_data, sampling_rate=1000)
        assert isinstance(result, float)
        assert 0 <= result <= 1
    
    def test_rho_e_calculator(self, sample_electrode_data):
        """Test RhoECalculator class."""
        calculator = RhoECalculator(sampling_rate=1000)
        result = calculator.compute(sample_electrode_data)
        assert isinstance(result, RhoEResult)
        assert hasattr(result, 'value')
        assert hasattr(result, 'spike_rate')
        assert hasattr(result, 'pattern_type')
    
    def test_rho_e_patterns(self):
        """Test different activity patterns."""
        calculator = RhoECalculator(sampling_rate=1000)
        
        # Test normal pattern
        normal_data = calculator.simulate_activity(duration=24, pattern='normal')
        normal_result = calculator.compute(normal_data, duration_hours=24)
        
        # Test dormant pattern
        dormant_data = calculator.simulate_activity(duration=24, pattern='dormant')
        dormant_result = calculator.compute(dormant_data, duration_hours=24)
        
        assert normal_result.value > dormant_result.value
        assert normal_result.pattern_type in ['normal', 'burst']
        assert dormant_result.pattern_type in ['dormant', 'normal']
    
    def test_rho_e_coherence(self, sample_electrode_data):
        """Test coherence calculation."""
        calculator = RhoECalculator(sampling_rate=1000)
        spikes = calculator.detect_spikes(sample_electrode_data)
        coherence = calculator.compute_coherence(sample_electrode_data, spikes)
        assert 0 <= coherence <= 1


class TestGradC:
    """Tests for ∇C - Chemotropic Navigation."""
    
    def test_compute_grad_c_basic(self):
        """Test basic ∇C computation."""
        from fungi_mycel.parameters.grad_c import GradCCalculator
        
        # Generate sample trajectory
        calculator = GradCCalculator()
        trajectory = calculator.simulate_trajectory(
            target_direction=(1, 0, 0),
            noise_level=5,
            length=50
        )
        
        result = calculator.compute(trajectory)
        assert 0 <= result.value <= 1
        assert hasattr(result, 'angular_error')
        assert hasattr(result, 'chemotactic_index')


class TestSER:
    """Tests for SER - Symbiotic Exchange Ratio."""
    
    def test_compute_ser_basic(self):
        """Test basic SER computation."""
        result = compute_ser(
            carbon_flux=120,
            phosphorus_flux=15,
            biome='temperate_broadleaf'
        )
        assert 0.5 <= result <= 2.0
    
    def test_ser_classification(self):
        """Test SER exchange classification."""
        from fungi_mycel.parameters.ser import SERCalculator
        
        calculator = SERCalculator(biome='temperate_broadleaf')
        
        # Balanced exchange
        balanced = calculator.compute(carbon_flux=100, phosphorus_flux=12)
        assert balanced.exchange_type == 'balanced'
        
        # Parasitic exchange
        parasitic = calculator.compute(carbon_flux=200, phosphorus_flux=10)
        assert parasitic.exchange_type == 'parasitic'
        
        # Plant-dominant exchange
        plant_dom = calculator.compute(carbon_flux=50, phosphorus_flux=20)
        assert plant_dom.exchange_type == 'plant_dominant'


class TestKTopo:
    """Tests for K_topo - Topological Expansion."""
    
    def test_compute_k_topo_basic(self, sample_binary_image):
        """Test basic K_topo computation."""
        result = compute_k_topo(sample_binary_image)
        assert 1.0 <= result <= 2.0
    
    def test_k_topo_network_types(self):
        """Test different network types."""
        from fungi_mycel.parameters.k_topo import KTopoCalculator
        
        calculator = KTopoCalculator()
        
        # Linear network
        linear = calculator.generate_test_pattern('linear')
        linear_result = calculator.compute_from_image(linear)
        assert linear_result.network_type == 'linear'
        assert linear_result.value < 1.4
        
        # Foraging network
        foraging = calculator.generate_test_pattern('foraging')
        foraging_result = calculator.compute_from_image(foraging)
        assert foraging_result.value > 1.5


class TestEa:
    """Tests for E_a - Adaptive Resilience."""
    
    def test_compute_e_a_basic(self):
        """Test basic E_a computation."""
        result = compute_e_a(
            control_growth=100,
            stressed_growth=60,
            stress_duration=48
        )
        assert 0 <= result <= 1
        assert result > 0.3
    
    def test_e_a_classification(self):
        """Test resilience classification."""
        from fungi_mycel.parameters.e_a import EACalculator
        
        calculator = EACalculator()
        
        # Resilient
        resilient = calculator.compute(control_growth=100, stressed_growth=85)
        assert resilient.resilience_class == 'RESILIENT'
        
        # Compromised
        compromised = calculator.compute(control_growth=100, stressed_growth=20)
        assert compromised.resilience_class == 'COMPROMISED'


class TestABI:
    """Tests for ABI - Biodiversity Amplification."""
    
    def test_compute_abi_basic(self):
        """Test basic ABI computation."""
        from fungi_mycel.parameters.abi import ABICalculator
        
        calculator = ABICalculator()
        rhizo, bulk = calculator.generate_test_data()
        result = calculator.compute_from_counts(rhizo, bulk)
        assert result.abi_value > 1.0
        assert result.shannon_rhizosphere > result.shannon_bulk


class TestBFS:
    """Tests for BFS - Biological Field Stability."""
    
    def test_compute_bfs_basic(self, sample_timeseries):
        """Test basic BFS computation."""
        timestamps, values = sample_timeseries
        result = compute_bfs(values, timestamps)
        assert 0 <= result <= 2.0
    
    def test_bfs_patterns(self):
        """Test different stability patterns."""
        from fungi_mycel.parameters.bfs import BFSCalculator
        
        calculator = BFSCalculator()
        
        # Stable pattern
        stable_t, stable_v = calculator.generate_test_timeseries('stable', n_points=20)
        stable_result = calculator.compute_from_timeseries(stable_v, stable_t)
        
        # Declining pattern
        decl_t, decl_v = calculator.generate_test_timeseries('declining', n_points=20)
        decl_result = calculator.compute_from_timeseries(decl_v, decl_t)
        
        assert stable_result.value > decl_result.value
        assert stable_result.stability_class in ['STABLE', 'VARIABLE']
        
    def test_tipping_point_detection(self, sample_timeseries):
        """Test tipping point detection."""
        from fungi_mycel.parameters.bfs import BFSCalculator
        
        calculator = BFSCalculator()
        timestamps, values = sample_timeseries
        
        # Add increasing variance to simulate critical slowing down
        values = [v * (1 + 0.02 * i) for i, v in enumerate(values)]
        
        indicators = calculator.detect_tipping_point(values, timestamps, window_size=10)
        assert 'variance_ratio' in indicators
        assert 'ar1_ratio' in indicators
