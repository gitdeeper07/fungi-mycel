"""
K_topo - Topological Expansion Rate

Characterizes the fractal geometry of mycelial network architecture through
the Hausdorff-Besicovitch fractal dimension. Networks are self-similar across
multiple spatial scales: from individual hyphae (5-50 μm) to entire territories
(1-100 m).

Physical mechanism: Self-similar branching patterns optimized for space-filling
efficiency and resource interception.

Units: Fractal dimension D_f (1.0-2.0)
Reference range: 1.35 - 1.95 D_f
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass
from scipy import ndimage
from skimage import io, filters, morphology, measure


@dataclass
class KTopoResult:
    """Container for K_topo calculation results."""
    
    value: float  # D_f fractal dimension
    box_counts: List[int]  # N(ε) for each scale
    box_sizes: List[float]  # ε values
    r_squared: float  # goodness of fit
    n_scales: int
    confidence: float  # 0-1
    network_type: str  # 'linear', 'sparse', 'foraging', 'space_filling'
    warnings: List[str] = None


class KTopoCalculator:
    """
    Calculator for Topological Expansion Rate (K_topo).
    
    K_topo = D_f · ln(N_ε) / ln(1/ε)
    
    where:
        D_f = Hausdorff-Besicovitch fractal dimension
        N_ε = number of boxes of side ε covering the network
        ε = box size
    """
    
    def __init__(self, min_box: float = 1.0, max_box: float = 1000.0):
        """
        Initialize K_topo calculator.
        
        Args:
            min_box: Minimum box size in μm
            max_box: Maximum box size in μm
        """
        self.min_box = min_box
        self.max_box = max_box
    
    def classify_network(self, d_f: float) -> str:
        """
        Classify network type based on fractal dimension.
        """
        if d_f < 1.35:
            return 'linear'  # Collapsed, extreme stress
        elif 1.35 <= d_f < 1.54:
            return 'sparse'  # Early establishment
        elif 1.54 <= d_f < 1.72:
            return 'transitional'
        elif 1.72 <= d_f < 1.85:
            return 'foraging'  # Normal intact state
        elif 1.85 <= d_f <= 1.95:
            return 'space_filling'  # Maximum foraging
        else:
            return 'unknown'
    
    def box_counting_2d(
        self,
        image: np.ndarray,  # Binary image (hyphae = 1, background = 0)
        box_sizes: Optional[List[float]] = None
    ) -> Tuple[List[int], List[float]]:
        """
        Perform 2D box-counting on binary image.
        
        Args:
            image: Binary image with hyphal structures
            box_sizes: List of box sizes to test
        
        Returns:
            (box_counts, box_sizes) for each scale
        """
        if box_sizes is None:
            # Generate logarithmic scale of box sizes
            box_sizes = np.logspace(
                np.log10(self.min_box),
                np.log10(min(self.max_box, min(image.shape))),
                num=20
            )
        
        box_counts = []
        valid_sizes = []
        
        for size in box_sizes:
            size_int = max(1, int(size))
            if size_int >= min(image.shape):
                continue
            
            # Count boxes containing hyphae
            n_boxes = 0
            for i in range(0, image.shape[0], size_int):
                for j in range(0, image.shape[1], size_int):
                    box = image[i:i+size_int, j:j+size_int]
                    if np.any(box):
                        n_boxes += 1
            
            if n_boxes > 0:
                box_counts.append(n_boxes)
                valid_sizes.append(size)
        
        return box_counts, valid_sizes
    
    def box_counting_3d(
        self,
        volume: np.ndarray,  # Binary 3D volume
        box_sizes: Optional[List[float]] = None
    ) -> Tuple[List[int], List[float]]:
        """
        Perform 3D box-counting on binary volume.
        """
        if box_sizes is None:
            box_sizes = np.logspace(
                np.log10(self.min_box),
                np.log10(min(self.max_box, min(volume.shape))),
                num=20
            )
        
        box_counts = []
        valid_sizes = []
        
        for size in box_sizes:
            size_int = max(1, int(size))
            if size_int >= min(volume.shape):
                continue
            
            # Count boxes containing hyphae
            n_boxes = 0
            for i in range(0, volume.shape[0], size_int):
                for j in range(0, volume.shape[1], size_int):
                    for k in range(0, volume.shape[2], size_int):
                        box = volume[i:i+size_int, j:j+size_int, k:k+size_int]
                        if np.any(box):
                            n_boxes += 1
            
            if n_boxes > 0:
                box_counts.append(n_boxes)
                valid_sizes.append(size)
        
        return box_counts, valid_sizes
    
    def compute_fractal_dimension(
        self,
        box_counts: List[int],
        box_sizes: List[float]
    ) -> Tuple[float, float]:
        """
        Compute fractal dimension from box-counting data.
        
        D_f = -lim(ε→0) [log N(ε) / log ε]
        
        Returns:
            (D_f, r_squared)
        """
        if len(box_counts) < 3:
            return 0.0, 0.0
        
        # Log-log transform
        log_eps = np.log(1.0 / np.array(box_sizes))
        log_n = np.log(box_counts)
        
        # Linear regression
        coeffs = np.polyfit(log_eps, log_n, 1)
        d_f = coeffs[0]
        
        # Calculate R²
        predicted = np.polyval(coeffs, log_eps)
        residuals = log_n - predicted
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((log_n - np.mean(log_n))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return d_f, r_squared
    
    def compute_from_image(
        self,
        image: np.ndarray,
        threshold: Optional[float] = None,
        is_3d: bool = False
    ) -> KTopoResult:
        """
        Compute K_topo from microscope image.
        
        Args:
            image: Microscope image (grayscale or binary)
            threshold: Threshold for binarization (auto if None)
            is_3d: Whether image is 3D volume
        
        Returns:
            KTopoResult object
        """
        # Convert to binary if needed
        if image.dtype != bool:
            if threshold is None:
                # Use Otsu threshold
                threshold = filters.threshold_otsu(image)
            binary = image > threshold
        else:
            binary = image
        
        # Perform morphological cleaning
        binary = morphology.remove_small_objects(binary, min_size=10)
        binary = morphology.remove_small_holes(binary, area_threshold=10)
        
        # Perform box-counting
        if is_3d:
            box_counts, box_sizes = self.box_counting_3d(binary)
        else:
            box_counts, box_sizes = self.box_counting_2d(binary)
        
        # Compute fractal dimension
        d_f, r_squared = self.compute_fractal_dimension(box_counts, box_sizes)
        
        # Classify network type
        network_type = self.classify_network(d_f)
        
        # Calculate confidence based on fit quality and coverage
        confidence = r_squared * min(1.0, len(box_counts) / 10)
        
        # Generate warnings
        warnings = []
        if d_f < 1.35:
            warnings.append("Critically low fractal dimension - network collapse")
        elif d_f < 1.54:
            warnings.append("Sparse network structure")
        
        if r_squared < 0.9:
            warnings.append("Poor fractal fit - possible multi-scale anomaly")
        
        if len(box_counts) < 5:
            warnings.append("Limited scale range for fractal analysis")
        
        return KTopoResult(
            value=d_f,
            box_counts=box_counts,
            box_sizes=box_sizes,
            r_squared=r_squared,
            n_scales=len(box_counts),
            confidence=confidence,
            network_type=network_type,
            warnings=warnings
        )
    
    def estimate_from_hyphal_density(
        self,
        hyphal_length: float,  # cm per cm³ soil
        branching_frequency: float,  # branches per mm
        exploration_type: str = 'medium'  # 'low', 'medium', 'high'
    ) -> float:
        """
        Estimate fractal dimension from basic network metrics.
        """
        # Base values
        base_d_f = {
            'low': 1.4,
            'medium': 1.6,
            'high': 1.8
        }.get(exploration_type, 1.6)
        
        # Adjust based on hyphal density
        density_factor = np.log10(hyphal_length / 100) / 2  # typical range 10-1000 cm/cm³
        density_factor = max(-0.2, min(0.2, density_factor))
        
        # Adjust based on branching
        branch_factor = 0.1 * (branching_frequency - 2)  # typical 1-3 branches/mm
        
        estimated = base_d_f + density_factor + branch_factor
        
        return min(1.95, max(1.2, estimated))
    
    @staticmethod
    def generate_test_pattern(pattern_type: str = 'foraging', size: int = 512) -> np.ndarray:
        """
        Generate test fractal patterns.
        """
        if pattern_type == 'linear':
            # Simple linear structure
            image = np.zeros((size, size))
            image[size//2, :] = 1
            
        elif pattern_type == 'sparse':
            # Sparse branching
            image = np.zeros((size, size))
            for i in range(0, size, 20):
                image[i, i:i+10] = 1
                image[i:i+10, i] = 1
                
        elif pattern_type == 'foraging':
            # Foraging network (D_f ~1.75)
            image = np.zeros((size, size))
            np.random.seed(42)
            for _ in range(1000):
                x = np.random.randint(0, size)
                y = np.random.randint(0, size)
                image[max(0, x-2):min(size, x+3), 
                      max(0, y-2):min(size, y+3)] = 1
                
        elif pattern_type == 'space_filling':
            # Space-filling (D_f ~1.9)
            image = np.ones((size, size))
            # Add some holes
            for i in range(0, size, 50):
                for j in range(0, size, 50):
                    if np.random.random() > 0.7:
                        image[i:i+20, j:j+20] = 0
        else:
            image = np.random.random((size, size)) > 0.9
        
        return image.astype(bool)


# Convenience function
def compute_k_topo(
    image: np.ndarray,
    **kwargs
) -> float:
    """
    Convenience function to compute K_topo.
    
    Args:
        image: Microscope image of mycelial network
        **kwargs: Additional parameters for KTopoCalculator.compute_from_image()
    
    Returns:
        Fractal dimension D_f
    """
    calculator = KTopoCalculator()
    result = calculator.compute_from_image(image, **kwargs)
    return result.value
