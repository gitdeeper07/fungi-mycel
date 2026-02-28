"""
FUNGI-MYCEL Data Loaders

Functions for loading various data formats used in the framework.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import json
import csv
import warnings

try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False

try:
    import netCDF4 as nc
    NETCDF_AVAILABLE = True
except ImportError:
    NETCDF_AVAILABLE = False

try:
    from skimage import io as skio
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


def load_electrode_data(
    file_path: Union[str, Path],
    sampling_rate: Optional[float] = None
) -> Tuple[np.ndarray, float]:
    """
    Load microelectrode array recording data.
    
    Args:
        file_path: Path to electrode data file
        sampling_rate: Sampling rate in Hz (if not embedded)
    
    Returns:
        (data_array, actual_sampling_rate)
        data_array shape: [time, electrodes]
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Handle different formats
    if file_path.suffix == '.npy':
        data = np.load(file_path)
        sr = sampling_rate or 1000.0  # default
        
    elif file_path.suffix == '.csv':
        df = pd.read_csv(file_path)
        data = df.values
        sr = sampling_rate or 1000.0
        
    elif file_path.suffix == '.h5' and HDF5_AVAILABLE:
        with h5py.File(file_path, 'r') as f:
            data = f['electrode_data'][:]
            sr = f.attrs.get('sampling_rate', sampling_rate or 1000.0)
    
    elif file_path.suffix == '.nc' and NETCDF_AVAILABLE:
        ds = nc.Dataset(file_path)
        data = ds.variables['electrode_data'][:]
        sr = ds.sampling_rate if hasattr(ds, 'sampling_rate') else (sampling_rate or 1000.0)
        ds.close()
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Ensure correct shape
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)
    
    return data, float(sr)


def load_parameters(
    file_path: Union[str, Path],
    site_id: Optional[str] = None,
    mnu_id: Optional[str] = None
) -> Dict[str, float]:
    """
    Load parameter values from file.
    
    Args:
        file_path: Path to parameter file
        site_id: Optional site ID filter
        mnu_id: Optional MNU ID filter
    
    Returns:
        Dictionary of parameter values
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Filter by ID if provided
        if site_id and 'site_id' in data and data['site_id'] != site_id:
            return {}
        
        if mnu_id and 'mnu_id' in data and data['mnu_id'] != mnu_id:
            return {}
        
        # Extract parameters
        if 'parameters' in data:
            return data['parameters']
        else:
            return {k: v for k, v in data.items() 
                   if k in ['eta_nw', 'rho_e', 'grad_c', 'ser', 
                           'k_topo', 'e_a', 'abi', 'bfs']}
    
    elif file_path.suffix == '.csv':
        df = pd.read_csv(file_path)
        
        # Filter by ID if provided
        if site_id and 'site_id' in df.columns:
            df = df[df['site_id'] == site_id]
        
        if mnu_id and 'mnu_id' in df.columns:
            df = df[df['mnu_id'] == mnu_id]
        
        if len(df) == 0:
            return {}
        
        # Take first row
        row = df.iloc[0]
        
        return {
            'eta_nw': row.get('eta_nw', 0.5),
            'rho_e': row.get('rho_e', 0.5),
            'grad_c': row.get('grad_c', 0.5),
            'ser': row.get('ser', 1.0),
            'k_topo': row.get('k_topo', 1.6),
            'e_a': row.get('e_a', 0.5),
            'abi': row.get('abi', 1.5),
            'bfs': row.get('bfs', 0.5),
        }
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def load_site_metadata(site_id: str) -> Dict[str, Any]:
    """
    Load metadata for a specific site.
    
    Args:
        site_id: Site identifier
    
    Returns:
        Site metadata dictionary
    """
    # This would normally load from database or file
    # Simplified version for now
    metadata = {
        'bialowieza-01': {
            'name': 'Białowieża National Park',
            'country': 'Poland',
            'biome': 'temperate_broadleaf',
            'established': 2007,
            'area_ha': 150,
            'dominant_trees': ['Fagus sylvatica', 'Quercus robur'],
            'dominant_fungi': ['Amanita muscaria', 'Cortinarius violaceus'],
            'coordinates': (52.7333, 23.8667),
            'elevation_m': 170,
            'mean_temp_c': 7.5,
            'mean_precip_mm': 650,
        },
        'oregon-armillaria-01': {
            'name': 'Malheur National Forest',
            'country': 'USA',
            'biome': 'boreal_conifer',
            'established': 2008,
            'area_ha': 965,
            'dominant_trees': ['Pinus ponderosa', 'Pseudotsuga menziesii'],
            'dominant_fungi': ['Armillaria ostoyae'],
            'coordinates': (44.1167, -118.6167),
            'elevation_m': 1500,
            'mean_temp_c': 6.2,
            'mean_precip_mm': 550,
        },
    }
    
    return metadata.get(site_id, {
        'name': 'Unknown',
        'biome': 'unknown',
        'established': 2020,
    })


def load_mnu_list(
    site_id: Optional[str] = None,
    biome: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Load list of Mycelial Network Units.
    
    Args:
        site_id: Optional site filter
        biome: Optional biome filter
        limit: Maximum number to return
    
    Returns:
        List of MNU metadata dictionaries
    """
    # This would normally load from database
    # Return dummy data for now
    mnus = []
    
    for i in range(min(limit, 10)):
        mnus.append({
            'mnu_id': f'MNU-2026-{i:04d}',
            'site_id': site_id or f'site-{i}',
            'sampling_date': '2026-02-15',
            'depth_cm': 10 + i,
            'soil_type': 'loam',
            'parameters_available': True,
        })
    
    return mnus


def load_sequence_data(
    file_path: Union[str, Path],
    format: str = 'fasta'
) -> List[Dict[str, str]]:
    """
    Load DNA/RNA/protein sequence data.
    
    Args:
        file_path: Path to sequence file
        format: 'fasta' or 'fastq'
    
    Returns:
        List of {'id': ..., 'sequence': ...} dictionaries
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sequences = []
    
    if format == 'fasta':
        with open(file_path, 'r') as f:
            current_id = None
            current_seq = []
            
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        sequences.append({
                            'id': current_id,
                            'sequence': ''.join(current_seq)
                        })
                    current_id = line[1:]
                    current_seq = []
                else:
                    current_seq.append(line)
            
            if current_id:
                sequences.append({
                    'id': current_id,
                    'sequence': ''.join(current_seq)
                })
    
    elif format == 'fastq':
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 4):
                if i + 3 < len(lines):
                    sequences.append({
                        'id': lines[i].strip()[1:],
                        'sequence': lines[i+1].strip(),
                        'quality': lines[i+3].strip()
                    })
    
    return sequences


def load_image_data(
    file_path: Union[str, Path],
    as_gray: bool = True
) -> np.ndarray:
    """
    Load microscope image data.
    
    Args:
        file_path: Path to image file
        as_gray: Convert to grayscale
    
    Returns:
        Image array
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if SKIMAGE_AVAILABLE:
        image = skio.imread(file_path, as_gray=as_gray)
    else:
        # Fallback to matplotlib
        import matplotlib.pyplot as plt
        image = plt.imread(file_path)
        if as_gray and len(image.shape) == 3:
            image = np.mean(image, axis=2)
    
    return image


def load_icpms_data(
    file_path: Union[str, Path]
) -> Dict[str, float]:
    """
    Load ICP-MS mineral dissolution data.
    
    Args:
        file_path: Path to ICP-MS data file
    
    Returns:
        Dictionary of element concentrations
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix == '.csv':
        df = pd.read_csv(file_path)
        if len(df) == 0:
            return {}
        
        # Take first row
        row = df.iloc[0]
        
        elements = {}
        for col in df.columns:
            if col not in ['sample_id', 'date', 'time']:
                try:
                    elements[col] = float(row[col])
                except (ValueError, TypeError):
                    pass
        
        return elements
    
    elif file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            return json.load(f)
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
