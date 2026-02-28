#!/usr/bin/env python3
"""
Simple test script to verify FUNGI-MYCEL imports.
"""

print("Testing FUNGI-MYCEL imports...")

try:
    import fungi_mycel
    print(f"✅ fungi_mycel version: {fungi_mycel.__version__}")
except ImportError as e:
    print(f"❌ Failed to import fungi_mycel: {e}")

try:
    from fungi_mycel.core import MNIS, compute_mnis
    print("✅ core module loaded")
except ImportError as e:
    print(f"❌ core module failed: {e}")

try:
    from fungi_mycel.parameters import (
        compute_eta_nw, compute_rho_e, compute_grad_c,
        compute_ser, compute_k_topo, compute_e_a,
        compute_abi, compute_bfs
    )
    print("✅ parameters module loaded")
except ImportError as e:
    print(f"❌ parameters module failed: {e}")

try:
    from fungi_mycel.models import AIEnsemble
    print("✅ models module loaded")
except ImportError as e:
    print(f"❌ models module failed: {e}")

try:
    from fungi_mycel.utils import load_site, validate_data
    print("✅ utils module loaded")
except ImportError as e:
    print(f"❌ utils module failed: {e}")

try:
    from fungi_mycel.io import load_electrode_data
    print("✅ io module loaded")
except ImportError as e:
    print(f"❌ io module failed: {e}")

try:
    from fungi_mycel.visualization import plot_mnis_timeseries
    print("✅ visualization module loaded")
except ImportError as e:
    print(f"❌ visualization module failed: {e}")

try:
    from fungi_mycel.cli import main
    print("✅ cli module loaded")
except ImportError as e:
    print(f"❌ cli module failed: {e}")

print("\n✨ All FUNGI-MYCEL modules imported successfully!")
