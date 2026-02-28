"""
FUNGI-MYCEL Plotting Functions

Functions for creating publication-quality figures.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = ['#2c5e2e', '#4a7a4c', '#6b8e6b', '#8ba38b', '#acb8ac']


def plot_mnis_timeseries(
    timestamps: List[float],
    mnis_values: List[float],
    site_name: Optional[str] = None,
    show_classes: bool = True,
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot MNIS time series with classification bands.
    
    Args:
        timestamps: List of timestamps (days)
        mnis_values: List of MNIS scores
        site_name: Optional site name for title
        show_classes: Whether to show classification bands
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot MNIS line
    ax.plot(timestamps, mnis_values, 'o-', color=COLORS[0], linewidth=2, markersize=6)
    
    # Add classification bands
    if show_classes:
        ax.axhspan(0.00, 0.25, alpha=0.1, color='green', label='EXCELLENT')
        ax.axhspan(0.25, 0.44, alpha=0.1, color='lightgreen', label='GOOD')
        ax.axhspan(0.44, 0.62, alpha=0.1, color='yellow', label='MODERATE')
        ax.axhspan(0.62, 0.80, alpha=0.1, color='orange', label='CRITICAL')
        ax.axhspan(0.80, 1.00, alpha=0.1, color='red', label='COLLAPSE')
    
    ax.set_xlabel('Time (days)')
    ax.set_ylabel('MNIS Score')
    ax.set_ylim(0, 1)
    
    if site_name:
        ax.set_title(f'MNIS Time Series - {site_name}')
    else:
        ax.set_title('Mycelial Network Intelligence Over Time')
    
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    return fig


def plot_parameter_radar(
    parameters: Dict[str, float],
    site_name: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 8)
) -> plt.Figure:
    """
    Create radar plot of all 8 parameters.
    
    Args:
        parameters: Dictionary of parameter values (normalized)
        site_name: Optional site name for title
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    # Parameter names and order
    param_names = ['η_NW', 'E_a', 'ρ_e', '∇C', 'SER', 'K_topo', 'ABI', 'BFS']
    param_keys = ['eta_nw', 'e_a', 'rho_e', 'grad_c', 'ser', 'k_topo', 'abi', 'bfs']
    
    # Get values
    values = [parameters.get(key, 0.5) for key in param_keys]
    
    # Number of variables
    N = len(param_names)
    
    # Compute angles for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Repeat values to close the loop
    values += values[:1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
    
    # Plot data
    ax.plot(angles, values, 'o-', linewidth=2, color=COLORS[0])
    ax.fill(angles, values, alpha=0.25, color=COLORS[0])
    
    # Set labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(param_names)
    
    # Set y limits
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'])
    ax.grid(True)
    
    # Add title
    if site_name:
        ax.set_title(f'Parameter Profile - {site_name}', pad=20)
    else:
        ax.set_title('Mycelial Network Parameter Profile', pad=20)
    
    return fig


def plot_parameter_correlation(
    data: Dict[str, List[float]],
    method: str = 'pearson',
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot correlation matrix between parameters.
    
    Args:
        data: Dictionary mapping parameter names to value lists
        method: Correlation method ('pearson', 'spearman')
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    if not SEABORN_AVAILABLE:
        raise ImportError("seaborn is required for correlation plots")
    
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(data)
    
    # Calculate correlation matrix
    corr = df.corr(method=method)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot heatmap
    sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0,
                square=True, linewidths=0.5, ax=ax,
                vmin=-1, vmax=1, cbar_kws={'shrink': 0.8})
    
    ax.set_title(f'Parameter Correlations ({method.capitalize()})')
    
    return fig


def plot_site_comparison(
    site_data: Dict[str, Dict[str, float]],
    parameter: str = 'mnis',
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Compare multiple sites.
    
    Args:
        site_data: Dictionary mapping site names to parameter values
        parameter: Parameter to compare
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    sites = list(site_data.keys())
    values = [site_data[site].get(parameter, 0) for site in sites]
    
    # Create bar colors based on values
    colors = []
    for v in values:
        if v < 0.25:
            colors.append('green')
        elif v < 0.44:
            colors.append('lightgreen')
        elif v < 0.62:
            colors.append('yellow')
        elif v < 0.80:
            colors.append('orange')
        else:
            colors.append('red')
    
    bars = ax.bar(sites, values, color=colors, edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, v in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{v:.3f}', ha='center', va='bottom', rotation=0)
    
    ax.set_xlabel('Site')
    ax.set_ylabel(f'{parameter.upper()} Value')
    ax.set_title(f'Site Comparison - {parameter.upper()}')
    ax.set_ylim(0, 1)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    return fig


def plot_electrode_activity(
    electrode_data: np.ndarray,
    sampling_rate: float = 1000.0,
    duration: Optional[float] = None,
    figsize: Tuple[int, int] = (14, 8)
) -> plt.Figure:
    """
    Plot raw electrode activity.
    
    Args:
        electrode_data: Array [time, electrodes]
        sampling_rate: Sampling rate in Hz
        duration: Duration to plot (seconds)
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    n_samples, n_electrodes = electrode_data.shape
    
    if duration:
        n_plot = min(int(duration * sampling_rate), n_samples)
    else:
        n_plot = min(5000, n_samples)  # Limit to 5000 points
    
    time = np.arange(n_plot) / sampling_rate
    
    fig, axes = plt.subplots(n_electrodes, 1, figsize=figsize, sharex=True)
    
    if n_electrodes == 1:
        axes = [axes]
    
    for i, ax in enumerate(axes):
        ax.plot(time, electrode_data[:n_plot, i], color=COLORS[i % len(COLORS)], linewidth=0.8)
        ax.set_ylabel(f'Electrode {i+1}')
        ax.set_ylim(-100, 100)  # Typical range ±100 mV
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time (seconds)')
    fig.suptitle('Multi-Electrode Array Recordings')
    
    plt.tight_layout()
    
    return fig


def plot_network_topology(
    binary_image: np.ndarray,
    figsize: Tuple[int, int] = (8, 8)
) -> plt.Figure:
    """
    Plot mycelial network topology.
    
    Args:
        binary_image: Binary image of network
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Original binary image
    axes[0].imshow(binary_image, cmap='gray', interpolation='nearest')
    axes[0].set_title('Binary Network')
    axes[0].axis('off')
    
    # Skeletonized version
    from skimage import morphology
    skeleton = morphology.skeletonize(binary_image)
    
    axes[1].imshow(skeleton, cmap='gray', interpolation='nearest')
    axes[1].set_title('Network Skeleton')
    axes[1].axis('off')
    
    plt.tight_layout()
    
    return fig


def plot_biome_distribution(
    biome_data: Dict[str, List[float]],
    parameter: str = 'mnis',
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot distribution across biomes.
    
    Args:
        biome_data: Dictionary mapping biome names to value lists
        parameter: Parameter being plotted
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    if not SEABORN_AVAILABLE:
        # Fallback to boxplot
        fig, ax = plt.subplots(figsize=figsize)
        
        biomes = list(biome_data.keys())
        data = [biome_data[b] for b in biomes]
        
        bp = ax.boxplot(data, labels=biomes, patch_artist=True)
        
        # Color boxes
        for patch, color in zip(bp['boxes'], COLORS[:len(biomes)]):
            patch.set_facecolor(color)
        
        ax.set_xlabel('Biome')
        ax.set_ylabel(f'{parameter.upper()} Value')
        ax.set_title(f'{parameter.upper()} Distribution Across Biomes')
        ax.grid(True, alpha=0.3)
        
    else:
        # Use seaborn for better violin plots
        import pandas as pd
        
        # Convert to long format
        rows = []
        for biome, values in biome_data.items():
            for v in values:
                rows.append({'Biome': biome, parameter: v})
        
        df = pd.DataFrame(rows)
        
        fig, ax = plt.subplots(figsize=figsize)
        sns.violinplot(data=df, x='Biome', y=parameter, palette=COLORS, ax=ax)
        ax.set_title(f'{parameter.upper()} Distribution Across Biomes')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig


def plot_early_warning(
    timestamps: List[float],
    mnis_values: List[float],
    variance: Optional[List[float]] = None,
    autocorr: Optional[List[float]] = None,
    threshold_date: Optional[float] = None,
    figsize: Tuple[int, int] = (12, 8)
) -> plt.Figure:
    """
    Plot early warning signals.
    
    Args:
        timestamps: Time points
        mnis_values: MNIS values
        variance: Rolling variance (optional)
        autocorr: Rolling autocorrelation (optional)
        threshold_date: Date of tipping point
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    n_plots = 1
    if variance is not None:
        n_plots += 1
    if autocorr is not None:
        n_plots += 1
    
    fig, axes = plt.subplots(n_plots, 1, figsize=figsize, sharex=True)
    
    if n_plots == 1:
        axes = [axes]
    
    plot_idx = 0
    
    # MNIS plot
    axes[plot_idx].plot(timestamps, mnis_values, 'o-', color=COLORS[0], linewidth=2)
    axes[plot_idx].set_ylabel('MNIS')
    axes[plot_idx].set_ylim(0, 1)
    axes[plot_idx].grid(True, alpha=0.3)
    
    if threshold_date:
        axes[plot_idx].axvline(x=threshold_date, color='red', linestyle='--', linewidth=2, label='Tipping Point')
        axes[plot_idx].legend()
    
    plot_idx += 1
    
    # Variance plot
    if variance is not None:
        axes[plot_idx].plot(timestamps[-len(variance):], variance, color=COLORS[1], linewidth=2)
        axes[plot_idx].set_ylabel('Variance')
        axes[plot_idx].grid(True, alpha=0.3)
        
        if threshold_date:
            axes[plot_idx].axvline(x=threshold_date, color='red', linestyle='--', linewidth=2)
        
        plot_idx += 1
    
    # Autocorrelation plot
    if autocorr is not None:
        axes[plot_idx].plot(timestamps[-len(autocorr):], autocorr, color=COLORS[2], linewidth=2)
        axes[plot_idx].set_ylabel('AR(1)')
        axes[plot_idx].set_ylim(0, 1)
        axes[plot_idx].grid(True, alpha=0.3)
        
        if threshold_date:
            axes[plot_idx].axvline(x=threshold_date, color='red', linestyle='--', linewidth=2)
        
        plot_idx += 1
    
    axes[-1].set_xlabel('Time (days)')
    fig.suptitle('Early Warning Signals of Critical Transition')
    
    plt.tight_layout()
    
    return fig


def create_dashboard_figure(
    mnis_result: Dict[str, Any],
    figsize: Tuple[int, int] = (15, 10)
) -> plt.Figure:
    """
    Create a combined dashboard figure.
    
    Args:
        mnis_result: MNIS result dictionary
        figsize: Figure size
    
    Returns:
        matplotlib Figure
    """
    fig = plt.figure(figsize=figsize)
    
    # Create grid for subplots
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Main MNIS gauge
    ax_main = fig.add_subplot(gs[0, :])
    mnis_score = mnis_result.get('mnis_score', 0.5)
    
    # Create horizontal bar gauge
    ax_main.barh([0], [mnis_score], color=COLORS[0], height=0.3)
    ax_main.barh([0], [1], left=[mnis_score], color='lightgray', height=0.3)
    ax_main.set_xlim(0, 1)
    ax_main.set_yticks([])
    ax_main.set_title(f"MNIS: {mnis_score:.3f} - {mnis_result.get('class', 'UNKNOWN')}")
    
    # Parameter radar
    ax_radar = fig.add_subplot(gs[1, 0], projection='polar')
    param_names = ['η_NW', 'E_a', 'ρ_e', '∇C', 'SER', 'K_topo', 'ABI', 'BFS']
    param_keys = ['eta_nw', 'e_a', 'rho_e', 'grad_c', 'ser', 'k_topo', 'abi', 'bfs']
    values = [mnis_result.get('normalized_params', {}).get(key, 0.5) for key in param_keys]
    
    angles = [n / 8 * 2 * np.pi for n in range(8)]
    angles += angles[:1]
    values += values[:1]
    
    ax_radar.plot(angles, values, 'o-', linewidth=2, color=COLORS[0])
    ax_radar.fill(angles, values, alpha=0.25, color=COLORS[0])
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(param_names, size=8)
    ax_radar.set_ylim(0, 1)
    ax_radar.set_title('Parameters', size=10)
    
    # Parameters table
    ax_table = fig.add_subplot(gs[1, 1:])
    ax_table.axis('off')
    
    table_data = []
    for key, name in zip(param_keys, param_names):
        raw = mnis_result.get('parameters', {}).get(key, 'N/A')
        norm = mnis_result.get('normalized_params', {}).get(key, 'N/A')
        if isinstance(raw, float):
            raw = f"{raw:.3f}"
        if isinstance(norm, float):
            norm = f"{norm:.3f}"
        table_data.append([name, raw, norm])
    
    table = ax_table.table(cellText=table_data,
                          colLabels=['Parameter', 'Raw', 'Normalized'],
                          loc='center',
                          cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    ax_table.set_title('Parameter Values', size=10)
    
    # Warnings
    if mnis_result.get('warning_flags'):
        ax_warnings = fig.add_subplot(gs[2, :])
        ax_warnings.axis('off')
        warnings_text = "\n".join([f"⚠️ {w}" for w in mnis_result['warning_flags']])
        ax_warnings.text(0.1, 0.5, warnings_text, transform=ax_warnings.transAxes,
                        fontsize=10, verticalalignment='center',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax_warnings.set_title('Warnings', size=10)
    
    fig.suptitle(f"Site: {mnis_result.get('site_id', 'Unknown')} | Biome: {mnis_result.get('biome', 'Unknown')}",
                fontsize=14, fontweight='bold')
    
    return fig
