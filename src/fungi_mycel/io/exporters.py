"""
FUNGI-MYCEL Data Exporters

Functions for exporting results in various formats.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import json
import csv
from datetime import datetime

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
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def export_to_csv(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    output_path: Union[str, Path],
    include_header: bool = True
):
    """
    Export data to CSV file.
    
    Args:
        data: Dictionary or list of dictionaries
        output_path: Output file path
        include_header: Whether to include header row
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(data, dict):
        data = [data]
    
    if not data:
        return
    
    # Get all field names
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if include_header:
            writer.writeheader()
        writer.writerows(data)


def export_to_json(
    data: Any,
    output_path: Union[str, Path],
    indent: int = 2
):
    """
    Export data to JSON file.
    
    Args:
        data: Data to export
        output_path: Output file path
        indent: JSON indentation
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=indent, default=str)


def export_to_netcdf(
    data: Dict[str, np.ndarray],
    output_path: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Export data to NetCDF file.
    
    Args:
        data: Dictionary of variable name -> array
        output_path: Output file path
        metadata: Global attributes
    """
    if not NETCDF_AVAILABLE:
        raise ImportError("netCDF4 is not available")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    ds = nc.Dataset(output_path, 'w', format='NETCDF4')
    
    # Add metadata
    if metadata:
        for key, value in metadata.items():
            ds.setncattr(key, value)
    
    ds.setncattr('created', datetime.now().isoformat())
    ds.setncattr('source', 'FUNGI-MYCEL v1.0.0')
    
    # Add dimensions and variables
    for name, array in data.items():
        # Create dimensions
        dims = []
        for i, dim_size in enumerate(array.shape):
            dim_name = f"{name}_dim_{i}"
            ds.createDimension(dim_name, dim_size)
            dims.append(dim_name)
        
        # Create variable
        var = ds.createVariable(name, array.dtype, dims)
        var[:] = array
    
    ds.close()


def export_to_hdf5(
    data: Dict[str, Any],
    output_path: Union[str, Path],
    compression: Optional[str] = 'gzip'
):
    """
    Export data to HDF5 file.
    
    Args:
        data: Dictionary of data to export
        output_path: Output file path
        compression: Compression algorithm
    """
    if not HDF5_AVAILABLE:
        raise ImportError("h5py is not available")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with h5py.File(output_path, 'w') as f:
        f.attrs['created'] = datetime.now().isoformat()
        f.attrs['source'] = 'FUNGI-MYCEL v1.0.0'
        
        def recursively_save(group, data_dict):
            for key, value in data_dict.items():
                if isinstance(value, dict):
                    subgroup = group.create_group(key)
                    recursively_save(subgroup, value)
                elif isinstance(value, (np.ndarray, list)):
                    data_array = np.array(value)
                    group.create_dataset(key, data=data_array, compression=compression)
                elif isinstance(value, (int, float, str, bool)):
                    group.attrs[key] = value
                else:
                    try:
                        group.create_dataset(key, data=np.array([value]), compression=compression)
                    except:
                        group.attrs[key] = str(value)
        
        recursively_save(f, data)


def export_report(
    mnis_results: Dict[str, Any],
    output_path: Union[str, Path],
    format: str = 'md'
):
    """
    Generate and export a human-readable report.
    
    Args:
        mnis_results: MNIS computation results
        output_path: Output file path
        format: 'md' (markdown), 'txt', or 'html'
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'md':
        with open(output_path, 'w') as f:
            f.write("# 🍄 FUNGI-MYCEL Network Intelligence Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            f.write("## 📊 MNIS Results\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| MNIS Score | {mnis_results.get('mnis_score', 'N/A'):.3f} |\n")
            f.write(f"| Class | {mnis_results.get('class', 'N/A')} |\n")
            f.write(f"| Biome | {mnis_results.get('biome', 'N/A')} |\n")
            if 'site_id' in mnis_results:
                f.write(f"| Site | {mnis_results['site_id']} |\n")
            if 'mnu_id' in mnis_results:
                f.write(f"| MNU | {mnis_results['mnu_id']} |\n")
            
            f.write("\n## 📈 Parameters\n\n")
            f.write("| Parameter | Raw Value | Normalized |\n")
            f.write("|-----------|-----------|------------|\n")
            
            params = mnis_results.get('parameters', {})
            norm_params = mnis_results.get('normalized_params', {})
            
            for param in ['eta_nw', 'rho_e', 'grad_c', 'ser', 'k_topo', 'e_a', 'abi', 'bfs']:
                raw = params.get(param, 'N/A')
                norm = norm_params.get(param, 'N/A')
                if isinstance(raw, float):
                    raw = f"{raw:.3f}"
                if isinstance(norm, float):
                    norm = f"{norm:.3f}"
                f.write(f"| {param} | {raw} | {norm} |\n")
            
            if 'warning_flags' in mnis_results and mnis_results['warning_flags']:
                f.write("\n## ⚠️ Warnings\n\n")
                for warning in mnis_results['warning_flags']:
                    f.write(f"- {warning}\n")
            
            f.write("\n---\n")
            f.write("*Report generated by FUNGI-MYCEL v1.0.0*\n")
    
    elif format == 'txt':
        with open(output_path, 'w') as f:
            f.write("FUNGI-MYCEL NETWORK INTELLIGENCE REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"MNIS Score: {mnis_results.get('mnis_score', 'N/A'):.3f}\n")
            f.write(f"Class: {mnis_results.get('class', 'N/A')}\n")
            f.write(f"Biome: {mnis_results.get('biome', 'N/A')}\n\n")
            
            f.write("Parameters:\n")
            f.write("-" * 30 + "\n")
            params = mnis_results.get('parameters', {})
            for param, value in params.items():
                if isinstance(value, float):
                    f.write(f"  {param}: {value:.3f}\n")
                else:
                    f.write(f"  {param}: {value}\n")
    
    elif format == 'html':
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>FUNGI-MYCEL Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c5e2e; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .warning {{ color: #ff6b6b; }}
    </style>
</head>
<body>
    <h1>🍄 FUNGI-MYCEL Network Intelligence Report</h1>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    
    <h2>📊 MNIS Results</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>MNIS Score</td><td>{mnis_results.get('mnis_score', 'N/A'):.3f}</td></tr>
        <tr><td>Class</td><td>{mnis_results.get('class', 'N/A')}</td></tr>
        <tr><td>Biome</td><td>{mnis_results.get('biome', 'N/A')}</td></tr>
    </table>
    
    <h2>📈 Parameters</h2>
    <table>
        <tr><th>Parameter</th><th>Raw Value</th><th>Normalized</th></tr>"""
        
        params = mnis_results.get('parameters', {})
        norm_params = mnis_results.get('normalized_params', {})
        for param in ['eta_nw', 'rho_e', 'grad_c', 'ser', 'k_topo', 'e_a', 'abi', 'bfs']:
            raw = params.get(param, 'N/A')
            norm = norm_params.get(param, 'N/A')
            html += f"<tr><td>{param}</td><td>{raw:.3f if isinstance(raw, float) else raw}</td><td>{norm:.3f if isinstance(norm, float) else norm}</td></tr>"
        
        if 'warning_flags' in mnis_results and mnis_results['warning_flags']:
            html += "</table>\n<h2>⚠️ Warnings</h2>\n<ul>"
            for warning in mnis_results['warning_flags']:
                html += f"<li class='warning'>{warning}</li>"
            html += "</ul>"
        
        html += "\n<hr><p><em>Generated by FUNGI-MYCEL v1.0.0</em></p></body></html>"
        
        with open(output_path, 'w') as f:
            f.write(html)
    
    else:
        raise ValueError(f"Unsupported format: {format}")


def export_plot(
    fig,
    output_path: Union[str, Path],
    format: str = 'png',
    dpi: int = 300,
    bbox_inches: str = 'tight'
):
    """
    Export matplotlib figure to file.
    
    Args:
        fig: matplotlib figure object
        output_path: Output file path
        format: 'png', 'pdf', 'svg', 'jpg'
        dpi: Resolution for raster formats
        bbox_inches: Bounding box setting
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is not available")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.savefig(output_path, format=format, dpi=dpi, bbox_inches=bbox_inches)
    plt.close(fig)


def export_mnis_batch(
    results: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    formats: List[str] = ['csv', 'json']
):
    """
    Export multiple MNIS results in batch.
    
    Args:
        results: List of MNIS result dictionaries
        output_dir: Output directory
        formats: List of formats to export
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if 'csv' in formats:
        export_to_csv(results, output_dir / f'mnis_batch_{timestamp}.csv')
    
    if 'json' in formats:
        export_to_json(results, output_dir / f'mnis_batch_{timestamp}.json')
    
    # Generate summary report
    summary = {
        'n_results': len(results),
        'mean_mnis': np.mean([r.get('mnis_score', 0) for r in results]),
        'std_mnis': np.std([r.get('mnis_score', 0) for r in results]),
        'classes': {}
    }
    
    for r in results:
        cls = r.get('class', 'UNKNOWN')
        summary['classes'][cls] = summary['classes'].get(cls, 0) + 1
    
    export_to_json(summary, output_dir / f'mnis_summary_{timestamp}.json')
