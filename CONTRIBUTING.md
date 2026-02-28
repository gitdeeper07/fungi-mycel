# 🍄 CONTRIBUTING TO FUNGI-MYCEL

First off, thank you for considering contributing to FUNGI-MYCEL! We welcome contributions from mycologists, bioelectrophysiologists, soil geochemists, data scientists, software engineers, Indigenous knowledge holders, and anyone passionate about understanding mycelial intelligence.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Types of Contributions](#types-of-contributions)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Data Contributions](#data-contributions)
- [Indigenous Knowledge Protocol](#indigenous-knowledge-protocol)
- [Adding New Parameters](#adding-new-parameters)
- [Reporting Issues](#reporting-issues)
- [Contact](#contact)

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@fungi-mycel.org.

Special attention is given to respecting Indigenous knowledge protocols and FPIC (Free, Prior and Informed Consent).

---

## Types of Contributions

### 🧪 Scientific Contributions
- New site data and MNU recordings
- Validation studies in unrepresented biomes
- Parameter refinement suggestions
- Hypothesis testing and experimental design

### 💻 Code Contributions
- MNIS calculation engine improvements
- AI ensemble architecture enhancements
- Signal processing algorithms for ρ_e
- Fractal dimension computation (K_topo)
- Dashboard and visualization tools

### 📊 Data Contributions
- Microelectrode array recordings (ρ_e)
- ICP-MS mineral dissolution data (η_NW)
- Confocal microscopy image stacks (K_topo, ∇C)
- 16S eDNA metabarcoding sequences (ABI)
- Isotope tracing data (SER)

### 📝 Documentation
- Parameter mathematical documentation
- Case study write-ups
- Translation to other languages
- Tutorials and examples

### 🌍 Indigenous Knowledge
- Traditional ecological knowledge (with proper FPIC)
- Indicator species observations
- Harvesting calendar validation
- Language translation of key concepts

---

## Getting Started

### Prerequisites

- **Python 3.8–3.11**
- **Git**
- **Basic knowledge of mycology or related field**
- **For code contributions**: Familiarity with numpy, scipy, pandas

### Setup Development Environment

```bash
# Fork the repository on GitLab/GitHub, then clone your fork
git clone https://gitlab.com/YOUR_USERNAME/fungi-mycel.git
cd fungi-mycel

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
pre-commit install
```

Verify Setup

```bash
# Run basic validation
python scripts/validate_environment.py

# Run tests
pytest tests/unit/ -v

# Check parameter correlations
python scripts/check_correlation.py --quick
```

---

Development Workflow

1. Create an issue describing your proposed changes
2. Discuss with maintainers to ensure alignment
3. Fork and branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   # or
   git checkout -b site/new-location-name
   ```
4. Make changes following our standards
5. Write/update tests for your changes
6. Run tests locally and ensure they pass
7. Commit with clear messages
8. Push to your fork
9. Open a Merge Request

Branch Naming

Prefix Purpose
feature/ New features (parameters, models)
fix/ Bug fixes
docs/ Documentation updates
site/ New site data additions
parameter/ Parameter refinements
perf/ Performance optimizations
indigenous/ Indigenous knowledge contributions

---

Pull Request Process

1. Update documentation for any changed functionality
2. Add tests for new features (coverage should not decrease)
3. Update CHANGELOG.md with your changes under "Unreleased"
4. Ensure CI passes (tests, linting, type checking)
5. Request review from maintainers
6. Address review feedback
7. Merge after approval and CI passes

PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] New feature (parameter/model)
- [ ] Bug fix
- [ ] Site data addition
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Indigenous knowledge (with FPIC)

## How Has This Been Tested?
Describe tests you added/ran

## MNIS Impact
- Parameters affected: [list]
- Expected accuracy change: [if applicable]

## Checklist
- [ ] Tests pass locally
- [ ] Docs updated
- [ ] CHANGELOG updated
- [ ] Code follows style guidelines
- [ ] Type hints added/updated
- [ ] FPIC obtained (if Indigenous knowledge)
```

---

Coding Standards

Python

· Format: Black (line length 88)
· Imports: isort with black profile
· Linting: ruff (see pyproject.toml for rules)
· Type Hints: Required for all public functions
· Docstrings: Google style

Example Parameter Module

```python
"""ρ_e - Bioelectrical Pulse Density parameter."""

from typing import Optional, Tuple, Union

import numpy as np
from scipy import signal

from fungi_mycel.core import ParameterBase


class BioelectricalPulseDensity(ParameterBase):
    """ρ_e: Bioelectrical Pulse Density.
    
    Measures the frequency and structure of electrical spike trains
    propagating through mycelial networks.
    
    Attributes:
        spike_rate: Number of spikes per hour (spikes·hour⁻¹)
        mean_amplitude: Mean spike amplitude (mV)
        coherence: Cross-electrode spike coherence (0-1)
    """
    
    def __init__(
        self,
        electrode_data: np.ndarray,
        sampling_rate: float = 1000.0,
        threshold_sigma: float = 3.0
    ):
        """Initialize ρ_e calculator.
        
        Args:
            electrode_data: 2D array [time, electrodes] with voltage recordings
            sampling_rate: Sampling rate in Hz (default: 1000)
            threshold_sigma: Spike detection threshold in sigma (default: 3.0)
            
        Raises:
            ValueError: If electrode_data is invalid
        """
        self.electrode_data = electrode_data
        self.sampling_rate = sampling_rate
        self.threshold_sigma = threshold_sigma
        
    def compute(self) -> float:
        """Compute normalized ρ_e value.
        
        Returns:
            ρ_e normalized to [0, 1] for MNIS integration
        """
        # Implementation
        spikes = self._detect_spikes()
        coherence = self._compute_coherence()
        
        rho_e_raw = np.mean([s.rate for s in spikes]) * np.mean([s.amplitude for s in spikes])
        rho_e_norm = self._normalize(rho_e_raw, biome=self.biome)
        
        return rho_e_norm
        
    def _detect_spikes(self) -> list:
        """Detect spikes using threshold algorithm."""
        # Spike detection implementation
        pass
        
    def _compute_coherence(self) -> float:
        """Compute wavelet cross-electrode coherence."""
        # Coherence computation
        pass
```

---

Testing Guidelines

Test Structure

```
tests/
├── conftest.py              # Fixtures
├── unit/                    # Unit tests
│   ├── parameters/
│   │   ├── test_rho_e.py
│   │   ├── test_k_topo.py
│   │   └── ...
│   └── core/
├── integration/             # Integration tests
│   ├── test_mnis_composite.py
│   └── test_ai_ensemble.py
├── hypothesis/              # Hypothesis validation (H1-H8)
│   ├── test_h1_accuracy.py
│   ├── test_h2_correlation.py
│   └── ...
├── benchmarks/              # Performance benchmarks
│   └── test_prediction_speed.py
└── fixtures/                # Test data
    ├── sample_electrode_data.npy
    ├── sample_confocal_images/
    └── sample_icpms_data.csv
```

Writing Tests

```python
import pytest
import numpy as np
from fungi_mycel.parameters import BioelectricalPulseDensity

def test_rho_e_computation(sample_electrode_data):
    """Test ρ_e computation with valid data."""
    rho_e = BioelectricalPulseDensity(sample_electrode_data)
    result = rho_e.compute()
    
    assert 0 <= result <= 1
    assert isinstance(result, float)

@pytest.mark.parametrize("amplitude,expected_range", [
    (10, (0.3, 0.5)),
    (50, (0.6, 0.8)),
    (100, (0.8, 1.0)),
])
def test_rho_e_amplitude_scaling(amplitude, expected_range):
    """Test that ρ_e scales correctly with amplitude."""
    # Create synthetic data
    data = generate_test_spikes(amplitude=amplitude)
    rho_e = BioelectricalPulseDensity(data)
    result = rho_e.compute()
    
    assert expected_range[0] <= result <= expected_range[1]

def test_h2_correlation():
    """Test H2: ρ_e × K_topo correlation r > 0.90."""
    from fungi_mycel.analysis import compute_correlation
    
    rho_e_values = load_test_rho_e()
    k_topo_values = load_test_k_topo()
    
    r, p = compute_correlation(rho_e_values, k_topo_values)
    
    assert r > 0.90
    assert p < 0.001
```

Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Hypothesis tests (H1-H8)
pytest tests/hypothesis/ -v

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=fungi_mycel --cov-report=html

# Benchmarks
pytest tests/benchmarks/ --benchmark-only

# Specific test
pytest tests/unit/parameters/test_rho_e.py::test_h2_correlation -v
```

---

Documentation

Building Documentation

```bash
cd docs
make html  # or make latexpdf for PDF
```

Documentation Standards

File Purpose
README.md Project overview, quick start
docs/parameters/ Detailed parameter documentation
docs/case_studies/ Extended case studies
docs/api/ API reference
examples/ Jupyter notebooks with examples

Docstring Style (Google)

```python
"""Summary line.

Extended description of function/module.

Args:
    arg1: Description of arg1
    arg2: Description of arg2

Returns:
    Description of return value

Raises:
    ValueError: Description of error condition

Examples:
    >>> result = function_name(10)
    >>> print(result)
    42
"""
```

---

Data Contributions

New Site Data

When adding data from a new monitoring site, include:

1. Site metadata (coordinates, biome, dominant species)
2. Electrode recordings (raw .npy or .csv files)
3. ICP-MS data (mineral dissolution rates)
4. Confocal images (if available)
5. 16S sequences (FASTA format)
6. Site photos (for documentation)

Data Format Requirements

Parameter Format Min Samples
ρ_e .npy, 16×T array, 1 kHz 72 hours
η_NW .csv with ICP-MS results 5 replicates
K_topo .tif image stacks 10 per site
∇C .csv with trajectory data 40 hyphal tips
SER .csv with isotope ratios 3 replicates
ABI .fasta 16S sequences 50,000+ reads

---

Indigenous Knowledge Protocol

FPIC Requirements

Any contribution involving Indigenous knowledge must:

1. Obtain FPIC - Document consent from community leadership
2. Provide attribution - Credit knowledge holders appropriately
3. Ensure benefit-sharing - Community should benefit from research
4. Respect data sovereignty - Community controls their knowledge
5. Community review - Allow review before publication

Contribution Process for Indigenous Knowledge

1. Contact indigenous@fungi-mycel.org to initiate
2. FPIC documentation - Provide proof of consent
3. Knowledge sharing - Work with community to document
4. Validation - Community reviews documentation
5. Attribution - Proper credit in AUTHORS.md

---

Adding New Parameters

If you propose a new parameter for MNIS:

1. Literature review - Demonstrate scientific basis
2. Physical independence - Show minimal correlation with existing parameters
3. Measurement protocol - Define how to measure it
4. Validation data - Provide dataset showing predictive power
5. Weight proposal - Suggest initial weight for composite

Parameter Template

```markdown
## Proposed Parameter: [NAME] ([SYMBOL])

### Description
[What it measures]

### Physical Mechanism
[How it works biologically/physically]

### Measurement Protocol
[Step-by-step instructions]

### Mathematical Definition
[Equation]

### Validation Evidence
[Data showing it predicts network outcomes]

### Correlation with Existing Parameters
[Show independence]
```

---

Reporting Issues

Bug Reports

Include:

· Clear title and description
· Steps to reproduce
· Expected vs actual behavior
· Environment details (OS, Python version)
· Logs or screenshots
· MNIS version

Feature Requests

Include:

· Use case description
· Expected behavior
· Scientific justification
· Potential implementation approach
· References to similar work

Data Issues

Include:

· Site ID and location
· Parameter affected
· Description of anomaly
· Raw data if possible

---

Contact

Purpose Contact
General inquiries gitdeeper@gmail.com
Code of Conduct conduct@fungi-mycel.org
Indigenous knowledge indigenous@fungi-mycel.org
Data contributions data@fungi-mycel.org
Scientific collaboration science@fungi-mycel.org

Project Repository: https://gitlab.com/gitdeeper07/fungi-mycel
Live Dashboard: https://fungi-mycel-science.netlify.app
DOI: 10.14293/FUNGI-MYCEL.2026.001

---

"The forest speaks. FUNGI-MYCEL translates." 🍄

Last Updated: February 2026
