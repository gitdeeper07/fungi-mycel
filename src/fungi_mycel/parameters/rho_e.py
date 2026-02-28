"""
ρ_e - Bioelectrical Pulse Density

Measures the frequency and structure of electrical spike trains propagating
through mycelial networks. This is the central parameter of the FUNGI-MYCEL
framework, directly measuring network communication activity.

Physical mechanism: Action-potential-like voltage spikes (10-100 mV amplitude,
1-50 second duration) propagating via voltage-gated ion channels at
0.5-10 mm/second.

Units: mV · spike · hour⁻¹ (normalized to [0,1])
Reference range: 0.20 - 0.75 normalized
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass
from scipy import signal
from scipy import stats
import warnings


@dataclass
class SpikeEvent:
    """Represents a single detected spike."""
    
    timestamp: float          # seconds
    amplitude: float          # mV
    duration: float           # seconds
    electrode_id: int
    rise_time: float          # seconds
    decay_time: float         # seconds


@dataclass
class RhoEResult:
    """Container for ρ_e calculation results."""
    
    value: float              # normalized ρ_e
    spike_rate: float         # spikes/hour
    mean_amplitude: float     # mV
    coherence: float          # cross-electrode coherence (0-1)
    spike_count: int
    active_electrodes: int
    dominant_frequency: float # Hz
    pattern_type: str         # 'normal', 'burst', 'stress', 'dormant'
    warnings: List[str] = None


class RhoECalculator:
    """
    Calculator for Bioelectrical Pulse Density (ρ_e).
    
    ρ_e = (1/N) · Σᵢ [V_mean,i · f_spike,i] + α · C_cross
    
    where:
        V_mean,i = mean spike amplitude at electrode i (mV)
        f_spike,i = spike rate at electrode i (spikes/hour)
        C_cross = cross-electrode spike coherence
        α = correlation weighting factor (0.35)
    """
    
    def __init__(self, sampling_rate: float = 1000.0):
        """
        Initialize ρ_e calculator.
        
        Args:
            sampling_rate: Sampling rate in Hz (default: 1000)
        """
        self.sampling_rate = sampling_rate
        self.alpha = 0.35  # correlation weighting factor from training set
        
    def detect_spikes(
        self,
        data: np.ndarray,           # 2D array [time, electrodes]
        threshold_sigma: float = 3.0,
        min_interval: float = 0.5,   # seconds
        artifact_rejection: bool = True
    ) -> List[List[SpikeEvent]]:
        """
        Detect spikes in multi-electrode recording.
        
        Args:
            data: Voltage recordings [time, electrodes]
            threshold_sigma: Detection threshold in standard deviations
            min_interval: Minimum interval between spikes (seconds)
            artifact_rejection: Whether to reject movement artifacts
            
        Returns:
            List of spikes per electrode
        """
        n_samples, n_electrodes = data.shape
        dt = 1.0 / self.sampling_rate
        min_interval_samples = int(min_interval / dt)
        
        spikes_per_electrode = []
        
        for electrode in range(n_electrodes):
            electrode_data = data[:, electrode]
            
            # Remove baseline
            baseline = np.median(electrode_data)
            detrended = electrode_data - baseline
            
            # Calculate threshold
            noise_std = np.std(detrended)
            threshold = threshold_sigma * noise_std
            
            # Find peaks
            peaks, properties = signal.find_peaks(
                detrended,
                height=threshold,
                distance=min_interval_samples,
                prominence=threshold/2,
                width=[5, 500]  # 5-500 samples width
            )
            
            electrode_spikes = []
            for i, peak_idx in enumerate(peaks):
                # Extract spike properties
                amplitude = properties['peak_heights'][i]
                width = properties['widths'][i] * dt
                
                # Find rise and decay times
                left = int(properties['left_ips'][i])
                right = int(properties['right_ips'][i])
                
                if left > 0 and right < len(detrended):
                    rise_time = (peak_idx - left) * dt
                    decay_time = (right - peak_idx) * dt
                else:
                    rise_time = width / 2
                    decay_time = width / 2
                
                # Artifact rejection (fast rise times < 5ms are likely artifacts)
                if artifact_rejection and rise_time < 0.005:
                    continue
                
                spike = SpikeEvent(
                    timestamp=peak_idx * dt,
                    amplitude=amplitude,
                    duration=width,
                    electrode_id=electrode,
                    rise_time=rise_time,
                    decay_time=decay_time
                )
                electrode_spikes.append(spike)
            
            spikes_per_electrode.append(electrode_spikes)
        
        return spikes_per_electrode
    
    def compute_coherence(
        self,
        data: np.ndarray,
        spikes_per_electrode: List[List[SpikeEvent]]
    ) -> float:
        """
        Compute cross-electrode spike coherence.
        
        Uses wavelet coherence to measure synchrony across the network.
        """
        n_electrodes = len(spikes_per_electrode)
        if n_electrodes < 2:
            return 0.0
        
        # Create spike time series for each electrode
        n_samples = len(data)
        spike_series = np.zeros((n_electrodes, n_samples))
        
        for electrode, spikes in enumerate(spikes_per_electrode):
            for spike in spikes:
                time_idx = int(spike.timestamp * self.sampling_rate)
                if time_idx < n_samples:
                    spike_series[electrode, time_idx] = spike.amplitude
        
        # Compute pairwise coherence
        coherence_sum = 0.0
        pair_count = 0
        
        for i in range(n_electrodes):
            for j in range(i+1, n_electrodes):
                # Use magnitude-squared coherence
                f, Cxy = signal.coherence(
                    spike_series[i],
                    spike_series[j],
                    fs=self.sampling_rate,
                    nperseg=min(1024, n_samples//10)
                )
                
                # Average coherence in relevant frequency band (0.001-0.1 Hz)
                mask = (f >= 0.001) & (f <= 0.1)
                if np.any(mask):
                    coherence_sum += np.mean(Cxy[mask])
                    pair_count += 1
        
        if pair_count > 0:
            return coherence_sum / pair_count
        else:
            return 0.0
    
    def classify_pattern(
        self,
        spike_rates: List[float],
        coherence: float
    ) -> str:
        """
        Classify the type of electrical activity pattern.
        
        Returns:
            'normal', 'burst', 'stress', or 'dormant'
        """
        mean_rate = np.mean(spike_rates) if spike_rates else 0
        rate_std = np.std(spike_rates) if len(spike_rates) > 1 else 0
        
        if mean_rate < 5:
            return 'dormant'
        elif mean_rate > 50 and coherence > 0.6:
            return 'burst'
        elif rate_std > mean_rate * 0.5:
            return 'stress'
        else:
            return 'normal'
    
    def compute(
        self,
        data: np.ndarray,                    # 2D array [time, electrodes]
        duration_hours: Optional[float] = None,
        threshold_sigma: float = 3.0,
        min_interval: float = 0.5
    ) -> RhoEResult:
        """
        Compute ρ_e from raw electrode recordings.
        
        Args:
            data: Voltage recordings [time, electrodes]
            duration_hours: Recording duration in hours (auto if None)
            threshold_sigma: Spike detection threshold
            min_interval: Minimum interval between spikes (seconds)
        
        Returns:
            RhoEResult object with calculated value and metadata
        """
        n_samples, n_electrodes = data.shape
        
        # Calculate duration
        if duration_hours is None:
            duration_hours = n_samples / self.sampling_rate / 3600
        
        # Detect spikes
        spikes_per_electrode = self.detect_spikes(
            data, threshold_sigma, min_interval
        )
        
        # Calculate per-electrode statistics
        spike_rates = []
        mean_amplitudes = []
        active_electrodes = 0
        
        for spikes in spikes_per_electrode:
            if spikes:
                spike_rate = len(spikes) / duration_hours
                mean_amplitude = np.mean([s.amplitude for s in spikes])
                
                spike_rates.append(spike_rate)
                mean_amplitudes.append(mean_amplitude)
                active_electrodes += 1
            else:
                spike_rates.append(0)
                mean_amplitudes.append(0)
        
        # Calculate network-level metrics
        if active_electrodes > 0:
            mean_spike_rate = np.mean([r for r in spike_rates if r > 0])
            mean_amplitude = np.mean([a for a in mean_amplitudes if a > 0])
        else:
            mean_spike_rate = 0
            mean_amplitude = 0
        
        # Calculate coherence
        coherence = self.compute_coherence(data, spikes_per_electrode)
        
        # Calculate raw ρ_e
        if active_electrodes > 0:
            rho_e_raw = mean_spike_rate * mean_amplitude + self.alpha * coherence * 100
        else:
            rho_e_raw = 0
        
        # Normalize to [0, 1] (empirical mapping)
        # Typical range: 0-200 for raw values
        rho_e_norm = min(1.0, max(0.0, rho_e_raw / 150))
        
        # Classify pattern
        pattern_type = self.classify_pattern(spike_rates, coherence)
        
        # Find dominant frequency (if enough activity)
        dominant_freq = 0.0
        if active_electrodes > 0 and len(spikes_per_electrode[0]) > 10:
            # Use first active electrode for frequency analysis
            for spikes in spikes_per_electrode:
                if len(spikes) > 10:
                    intervals = np.diff([s.timestamp for s in spikes])
                    if len(intervals) > 1:
                        # Convert intervals to frequency
                        freqs = 1.0 / intervals
                        dominant_freq = np.median(freqs[freqs < 0.1])  # Focus on <0.1 Hz
                    break
        
        # Generate warnings
        warnings = []
        if rho_e_norm < 0.2:
            warnings.append("Critically low electrical activity")
        elif rho_e_norm < 0.35:
            warnings.append("Reduced electrical activity - possible stress")
        
        if coherence < 0.3 and active_electrodes > 1:
            warnings.append("Low network coherence - possible fragmentation")
        
        if pattern_type == 'stress':
            warnings.append("Stress pattern detected in electrical activity")
        elif pattern_type == 'burst':
            warnings.append("Burst activity detected - possible awakening event")
        
        return RhoEResult(
            value=rho_e_norm,
            spike_rate=mean_spike_rate,
            mean_amplitude=mean_amplitude,
            coherence=coherence,
            spike_count=sum(len(s) for s in spikes_per_electrode),
            active_electrodes=active_electrodes,
            dominant_frequency=dominant_freq,
            pattern_type=pattern_type,
            warnings=warnings
        )
    
    @staticmethod
    def simulate_activity(
        duration: float = 72,           # hours
        pattern: str = 'normal',
        n_electrodes: int = 16,
        sampling_rate: float = 1000.0
    ) -> np.ndarray:
        """
        Simulate electrical activity for testing.
        
        Args:
            duration: Recording duration in hours
            pattern: 'normal', 'burst', 'stress', 'dormant'
            n_electrodes: Number of electrodes
            sampling_rate: Sampling rate in Hz
        
        Returns:
            Simulated data array [time, electrodes]
        """
        n_samples = int(duration * 3600 * sampling_rate)
        dt = 1.0 / sampling_rate
        t = np.arange(n_samples) * dt
        
        data = np.zeros((n_samples, n_electrodes))
        
        # Base parameters
        if pattern == 'dormant':
            base_rate = 2  # spikes/hour
            amplitude = 20  # mV
        elif pattern == 'normal':
            base_rate = 15
            amplitude = 40
        elif pattern == 'burst':
            base_rate = 30
            amplitude = 60
        elif pattern == 'stress':
            base_rate = 25
            amplitude = 30
        else:
            base_rate = 15
            amplitude = 40
        
        # Generate spikes for each electrode
        for electrode in range(n_electrodes):
            n_spikes = int(base_rate * duration * (0.8 + 0.4 * np.random.random()))
            spike_times = np.sort(np.random.uniform(0, duration*3600, n_spikes))
            
            for spike_time in spike_times:
                spike_idx = int(spike_time * sampling_rate)
                if spike_idx >= n_samples:
                    continue
                
                # Create spike waveform (double exponential)
                spike_duration = 0.1  # seconds
                spike_len = int(spike_duration * sampling_rate)
                start = max(0, spike_idx - spike_len//2)
                end = min(n_samples, spike_idx + spike_len//2)
                
                if end > start:
                    idx = np.arange(end - start)
                    # Double exponential spike shape
                    spike_shape = amplitude * (
                        np.exp(-idx / (spike_len/10)) -
                        np.exp(-idx / (spike_len/20))
                    )
                    data[start:end, electrode] += spike_shape[:end-start]
            
            # Add background noise
            data[:, electrode] += np.random.normal(0, 5, n_samples)
        
        return data


# Convenience function
def compute_rho_e(
    data: np.ndarray,
    sampling_rate: float = 1000.0,
    **kwargs
) -> float:
    """
    Convenience function to compute ρ_e.
    
    Args:
        data: Voltage recordings [time, electrodes]
        sampling_rate: Sampling rate in Hz
        **kwargs: Additional parameters for RhoECalculator.compute()
    
    Returns:
        Normalized ρ_e value
    """
    calculator = RhoECalculator(sampling_rate=sampling_rate)
    result = calculator.compute(data, **kwargs)
    return result.value
