"""
ABI - Biodiversity Amplification Index

Quantifies the ecological service that mycelial networks provide to the surrounding
soil community - the amplification of microbial diversity in the rhizosphere
relative to bulk soil.

Physical mechanism: Hyphal exudates (organic acids, sugars, amino acids) create
a zone of elevated metabolic activity supporting richer microbial communities.

Units: Ratio H'_rhizosphere / H'_bulk_soil
Reference range: 1.00 - 2.20 (mean intact sites: 1.84)
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple, List
from dataclasses import dataclass
import warnings

try:
    from skbio.diversity import alpha_diversity
    from skbio import read as read_sequence
    SKBIO_AVAILABLE = True
except ImportError:
    SKBIO_AVAILABLE = False
    warnings.warn("scikit-bio not available - using simplified diversity calculations")


@dataclass
class BiodiversityResult:
    """Container for biodiversity calculations."""
    
    shannon_rhizosphere: float  # H' rhizosphere
    shannon_bulk: float  # H' bulk soil
    abi_value: float  # ABI ratio
    richness_rhizosphere: int  # OTU/ASV count
    richness_bulk: int
    evenness_rhizosphere: float  # Pielou's evenness
    evenness_bulk: float
    n_samples_rhizosphere: int
    n_samples_bulk: int
    sequencing_depth: int
    warnings: List[str] = None


class ABICalculator:
    """
    Calculator for Biodiversity Amplification Index (ABI).
    
    ABI = H'_rhizosphere / H'_bulk_soil
    
    where H' is the Shannon diversity index computed from 16S rRNA
    metabarcoding of matched rhizosphere and bulk soil samples.
    """
    
    def __init__(self, sequencing_depth: int = 50000):
        """
        Initialize ABI calculator.
        
        Args:
            sequencing_depth: Target sequencing depth for rarefaction
        """
        self.sequencing_depth = sequencing_depth
    
    def calculate_shannon(
        self,
        abundance_counts: List[int]
    ) -> float:
        """
        Calculate Shannon diversity index from abundance counts.
        
        H' = -Σ p_i · ln(p_i)
        where p_i = proportion of species i
        """
        total = sum(abundance_counts)
        if total == 0:
            return 0.0
        
        proportions = [c / total for c in abundance_counts if c > 0]
        
        if not proportions:
            return 0.0
        
        shannon = -sum(p * np.log(p) for p in proportions)
        return shannon
    
    def calculate_evenness(
        self,
        shannon: float,
        n_species: int
    ) -> float:
        """Calculate Pielou's evenness (J' = H' / ln(S))."""
        if n_species <= 1:
            return 1.0
        return shannon / np.log(n_species)
    
    def rarefy(
        self,
        counts: List[List[int]],
        depth: Optional[int] = None
    ) -> List[List[int]]:
        """
        Perform rarefaction to standardize sequencing depth.
        
        Args:
            counts: List of samples, each with list of OTU abundances
            depth: Target depth (default: self.sequencing_depth)
        
        Returns:
            Rarefied counts
        """
        if depth is None:
            depth = self.sequencing_depth
        
        rarefied = []
        for sample in counts:
            total = sum(sample)
            if total < depth:
                # Sample too shallow - use original
                rarefied.append(sample)
                continue
            
            # Simple rarefaction by random subsampling
            # In production, use skbio's rarefaction
            indices = []
            for i, count in enumerate(sample):
                indices.extend([i] * count)
            
            if len(indices) > depth:
                subsample = np.random.choice(indices, size=depth, replace=False)
                new_counts = [0] * len(sample)
                for idx in subsample:
                    new_counts[idx] += 1
                rarefied.append(new_counts)
            else:
                rarefied.append(sample)
        
        return rarefied
    
    def compute_from_counts(
        self,
        rhizosphere_counts: List[List[int]],  # Multiple samples
        bulk_counts: List[List[int]],  # Multiple samples
        otu_names: Optional[List[str]] = None,
        rarefy: bool = True
    ) -> BiodiversityResult:
        """
        Compute ABI from OTU/ASV abundance counts.
        
        Args:
            rhizosphere_counts: List of samples from rhizosphere
            bulk_counts: List of samples from bulk soil
            otu_names: Names of OTUs/ASVs
            rarefy: Whether to rarefy to standard depth
        
        Returns:
            BiodiversityResult object
        """
        if rarefy:
            # Combine all samples for rarefaction
            all_counts = rhizosphere_counts + bulk_counts
            rarefied_all = self.rarefy(all_counts)
            n_rhizo = len(rhizosphere_counts)
            rhizosphere_counts = rarefied_all[:n_rhizo]
            bulk_counts = rarefied_all[n_rhizo:]
        
        # Calculate diversity for each sample
        rhizo_shannons = []
        rhizo_richness = []
        bulk_shannons = []
        bulk_richness = []
        
        for sample in rhizosphere_counts:
            # Remove zeros
            non_zero = [c for c in sample if c > 0]
            if non_zero:
                shannon = self.calculate_shannon(non_zero)
                richness = len(non_zero)
                rhizo_shannons.append(shannon)
                rhizo_richness.append(richness)
        
        for sample in bulk_counts:
            non_zero = [c for c in sample if c > 0]
            if non_zero:
                shannon = self.calculate_shannon(non_zero)
                richness = len(non_zero)
                bulk_shannons.append(shannon)
                bulk_richness.append(richness)
        
        # Average across samples
        if rhizo_shannons:
            mean_rhizo_shannon = np.mean(rhizo_shannons)
            mean_rhizo_richness = np.mean(rhizo_richness)
            rhizo_evenness = self.calculate_evenness(
                mean_rhizo_shannon, mean_rhizo_richness
            )
        else:
            mean_rhizo_shannon = 0
            mean_rhizo_richness = 0
            rhizo_evenness = 0
        
        if bulk_shannons:
            mean_bulk_shannon = np.mean(bulk_shannons)
            mean_bulk_richness = np.mean(bulk_richness)
            bulk_evenness = self.calculate_evenness(
                mean_bulk_shannon, mean_bulk_richness
            )
        else:
            mean_bulk_shannon = 0
            mean_bulk_richness = 0
            bulk_evenness = 0
        
        # Calculate ABI
        if mean_bulk_shannon > 0:
            abi = mean_rhizo_shannon / mean_bulk_shannon
        else:
            abi = 1.0
        
        # Generate warnings
        warnings = []
        if abi < 1.3:
            warnings.append("Low biodiversity amplification - possible hyphal exudate dysfunction")
        elif abi < 1.5:
            warnings.append("Moderate biodiversity amplification - below optimal")
        
        if mean_rhizo_richness < 50:
            warnings.append("Very low rhizosphere richness - severe degradation")
        elif mean_rhizo_richness < 100:
            warnings.append("Low rhizosphere richness")
        
        if mean_bulk_shannon < 2.0:
            warnings.append("Low bulk soil diversity - site may be degraded")
        
        return BiodiversityResult(
            shannon_rhizosphere=mean_rhizo_shannon,
            shannon_bulk=mean_bulk_shannon,
            abi_value=abi,
            richness_rhizosphere=int(mean_rhizo_richness),
            richness_bulk=int(mean_bulk_richness),
            evenness_rhizosphere=rhizo_evenness,
            evenness_bulk=bulk_evenness,
            n_samples_rhizosphere=len(rhizosphere_counts),
            n_samples_bulk=len(bulk_counts),
            sequencing_depth=self.sequencing_depth,
            warnings=warnings
        )
    
    def estimate_from_soil_parameters(
        self,
        organic_matter: float,  # %
        ph: float,
        nitrogen: float,  # mg/kg
        fungal_biomass: float  # μg C/g soil
    ) -> float:
        """
        Estimate ABI from soil parameters when sequencing unavailable.
        """
        # Base amplification
        base_abi = 1.5
        
        # Organic matter increases ABI
        om_factor = 1.0 + 0.1 * np.log1p(organic_matter)
        
        # pH effect (optimal 5.5-7.0)
        if 5.5 <= ph <= 7.0:
            ph_factor = 1.0
        else:
            ph_factor = 1.0 - 0.1 * abs(ph - 6.25)
        
        # Nitrogen effect (excess N reduces ABI)
        n_factor = 1.0 - 0.2 * (nitrogen / 100) if nitrogen > 50 else 1.0
        
        # Fungal biomass directly related
        biomass_factor = 1.0 + 0.3 * (fungal_biomass / 200)
        
        estimated = base_abi * om_factor * ph_factor * n_factor * biomass_factor
        
        return min(2.5, max(1.0, estimated))
    
    @staticmethod
    def generate_test_data(
        n_rhizo: int = 10,
        n_bulk: int = 10,
        n_otus: int = 200
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Generate test data for ABI calculation.
        
        Rhizosphere has higher diversity than bulk soil.
        """
        np.random.seed(42)
        
        rhizosphere = []
        bulk = []
        
        # Rhizosphere: more OTUs, more even distribution
        for _ in range(n_rhizo):
            # Log-normal distribution
            abundances = np.random.lognormal(mean=2, sigma=1, size=n_otus)
            # Add zeros (some OTUs absent)
            abundances[np.random.random(n_otus) < 0.3] = 0
            abundances = (abundances / abundances.sum() * 50000).astype(int)
            rhizosphere.append(abundances.tolist())
        
        # Bulk soil: fewer OTUs, more skewed
        for _ in range(n_bulk):
            abundances = np.random.lognormal(mean=1.5, sigma=1.5, size=n_otus)
            abundances[np.random.random(n_otus) < 0.5] = 0
            abundances = (abundances / abundances.sum() * 30000).astype(int)
            bulk.append(abundances.tolist())
        
        return rhizosphere, bulk


# Convenience function
def compute_abi(
    rhizosphere_counts: List[List[int]],
    bulk_counts: List[List[int]],
    **kwargs
) -> float:
    """
    Convenience function to compute ABI.
    
    Args:
        rhizosphere_counts: List of samples from rhizosphere
        bulk_counts: List of samples from bulk soil
        **kwargs: Additional parameters for ABICalculator.compute_from_counts()
    
    Returns:
        ABI value
    """
    calculator = ABICalculator()
    result = calculator.compute_from_counts(rhizosphere_counts, bulk_counts, **kwargs)
    return result.abi_value
