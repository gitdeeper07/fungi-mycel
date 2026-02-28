"""
FUNGI-MYCEL Interactive Dashboard

Provides interactive visualization and monitoring capabilities.
Supports both local development and deployment (Streamlit/Dash).
"""

import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
import json
import warnings

# Try importing dashboard frameworks
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class MNISDashboard:
    """
    Interactive dashboard for MNIS visualization and monitoring.
    
    Supports both Streamlit and Dash backends.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize dashboard.
        
        Args:
            data_dir: Directory containing site data
        """
        self.data_dir = data_dir or Path('./data')
        self.sites_cache = {}
        self.mnus_cache = {}
        
        # Color scheme
        self.colors = {
            'excellent': '#00cc66',
            'good': '#99cc00',
            'moderate': '#ffcc00',
            'critical': '#ff9900',
            'collapse': '#ff3300',
            'background': '#f8f9fa',
            'text': '#212529',
        }
    
    def load_site_list(self) -> List[Dict[str, Any]]:
        """Load list of available sites."""
        # This would load from database in production
        sites = [
            {'id': 'bialowieza-01', 'name': 'Białowieża Forest', 'country': 'Poland', 'biome': 'temperate_broadleaf', 'mnus': 124},
            {'id': 'bialowieza-02', 'name': 'Białowieża Reserve', 'country': 'Poland', 'biome': 'temperate_broadleaf', 'mnus': 98},
            {'id': 'oregon-armillaria-01', 'name': 'Malheur NF', 'country': 'USA', 'biome': 'boreal_conifer', 'mnus': 256},
            {'id': 'amazon-terra-preta-01', 'name': 'Terra Preta Site 1', 'country': 'Brazil', 'biome': 'tropical_montane', 'mnus': 187},
            {'id': 'caledonian-01', 'name': 'Caledonian Pine', 'country': 'Scotland', 'biome': 'temperate_broadleaf', 'mnus': 76},
            {'id': 'sudbury-01', 'name': 'Sudbury Recovery', 'country': 'Canada', 'biome': 'boreal_conifer', 'mnus': 145},
            {'id': 'cascade-04', 'name': 'Cascade Range', 'country': 'USA', 'biome': 'boreal_conifer', 'mnus': 203},
            {'id': 'sapmi-01', 'name': 'Sápmi Birch', 'country': 'Norway', 'biome': 'subarctic_birch', 'mnus': 67},
            {'id': 'hokkaido-01', 'name': 'Hokkaido Forest', 'country': 'Japan', 'biome': 'temperate_broadleaf', 'mnus': 89},
            {'id': 'andalucia-01', 'name': 'Andalucía Woodland', 'country': 'Spain', 'biome': 'mediterranean_woodland', 'mnus': 112},
        ]
        return sites
    
    def get_site_mnus(self, site_id: str) -> List[Dict[str, Any]]:
        """Get MNUs for a specific site."""
        # Simplified - would load from database
        mnus = []
        for i in range(10):
            mnus.append({
                'mnu_id': f'MNU-{site_id}-{i:04d}',
                'date': f'2026-02-{15+i}',
                'mnis': np.random.uniform(0.2, 0.8),
                'parameters': {
                    'eta_nw': np.random.uniform(0.3, 0.9),
                    'rho_e': np.random.uniform(0.2, 0.8),
                    'k_topo': np.random.uniform(1.3, 1.9),
                }
            })
        return mnus
    
    def create_streamlit_app(self):
        """Create Streamlit dashboard app."""
        if not STREAMLIT_AVAILABLE:
            raise ImportError("streamlit is required for this dashboard")
        
        st.set_page_config(
            page_title="FUNGI-MYCEL Dashboard",
            page_icon="🍄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header
        st.title("🍄 FUNGI-MYCEL Network Intelligence Dashboard")
        st.markdown("---")
        
        # Sidebar
        st.sidebar.header("Controls")
        
        sites = self.load_site_list()
        site_names = [f"{s['name']} ({s['country']})" for s in sites]
        site_ids = [s['id'] for s in sites]
        
        selected_site_idx = st.sidebar.selectbox(
            "Select Site",
            range(len(site_names)),
            format_func=lambda x: site_names[x]
        )
        selected_site_id = site_ids[selected_site_idx]
        selected_site = sites[selected_site_idx]
        
        # Time range
        st.sidebar.subheader("Time Range")
        start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2025-01-01"))
        end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2026-02-28"))
        
        # Parameters to display
        st.sidebar.subheader("Parameters")
        show_params = st.sidebar.multiselect(
            "Select Parameters",
            ['eta_nw', 'rho_e', 'grad_c', 'ser', 'k_topo', 'e_a', 'abi', 'bfs'],
            default=['eta_nw', 'rho_e', 'k_topo']
        )
        
        # Main content area
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total MNUs", selected_site['mnus'])
        
        with col2:
            # Average MNIS (simulated)
            avg_mnis = 0.47
            st.metric("Avg MNIS", f"{avg_mnis:.3f}", "0.02")
        
        with col3:
            # Active alerts
            alerts = np.random.randint(0, 3)
            st.metric("Active Alerts", alerts, delta=-1 if alerts > 0 else 0)
        
        with col4:
            # Data coverage
            coverage = 94
            st.metric("Coverage", f"{coverage}%", "2%")
        
        st.markdown("---")
        
        # MNIS Time Series
        st.subheader(f"📈 MNIS Time Series - {selected_site['name']}")
        
        # Generate sample data
        dates = pd.date_range(start=start_date, end=end_date, periods=50)
        mnis_values = 0.4 + 0.1 * np.sin(np.linspace(0, 4*np.pi, 50)) + 0.05 * np.random.randn(50)
        mnis_values = np.clip(mnis_values, 0.1, 0.9)
        
        # Create plot
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=('MNIS Score', 'Parameter Values'),
                            vertical_spacing=0.1)
        
        # MNIS trace
        fig.add_trace(
            go.Scatter(x=dates, y=mnis_values, mode='lines+markers',
                      name='MNIS', line=dict(color='#2c5e2e', width=2)),
            row=1, col=1
        )
        
        # Add threshold bands
        fig.add_hrect(y0=0, y1=0.25, line_width=0, fillcolor="green", opacity=0.1, row=1, col=1)
        fig.add_hrect(y0=0.25, y1=0.44, line_width=0, fillcolor="lightgreen", opacity=0.1, row=1, col=1)
        fig.add_hrect(y0=0.44, y1=0.62, line_width=0, fillcolor="yellow", opacity=0.1, row=1, col=1)
        fig.add_hrect(y0=0.62, y1=0.80, line_width=0, fillcolor="orange", opacity=0.1, row=1, col=1)
        fig.add_hrect(y0=0.80, y1=1.0, line_width=0, fillcolor="red", opacity=0.1, row=1, col=1)
        
        # Parameter traces
        colors = ['#4a7a4c', '#6b8e6b', '#8ba38b', '#acb8ac']
        for i, param in enumerate(show_params):
            param_values = 0.5 + 0.1 * np.random.randn(50)
            param_values = np.clip(param_values, 0.1, 0.9)
            fig.add_trace(
                go.Scatter(x=dates, y=param_values, mode='lines',
                          name=param, line=dict(color=colors[i % len(colors)])),
                row=2, col=1
            )
        
        fig.update_layout(height=600, showlegend=True, hovermode='x unified')
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="MNIS", row=1, col=1, range=[0, 1])
        fig.update_yaxes(title_text="Value", row=2, col=1, range=[0, 1])
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Parameter Radar
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🕸️ Current Parameter Profile")
            
            # Get latest parameters
            latest_params = {
                'η_NW': 0.72,
                'E_a': 0.65,
                'ρ_e': 0.68,
                '∇C': 0.71,
                'SER': 1.05,
                'K_topo': 1.72,
                'ABI': 1.84,
                'BFS': 0.58,
            }
            
            # Normalize for radar
            norm_params = {
                'η_NW': latest_params['η_NW'],
                'E_a': latest_params['E_a'],
                'ρ_e': latest_params['ρ_e'],
                '∇C': latest_params['∇C'],
                'SER': 1.0 - abs(latest_params['SER'] - 1.0) / 0.6,  # Normalize SER
                'K_topo': (latest_params['K_topo'] - 1.28) / (1.88 - 1.28),
                'ABI': (latest_params['ABI'] - 1.0) / (2.2 - 1.0),
                'BFS': latest_params['BFS'],
            }
            
            # Create radar chart
            categories = list(norm_params.keys())
            values = list(norm_params.values())
            values += values[:1]  # Close the loop
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name='Current State',
                line=dict(color='#2c5e2e', width=2)
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Site Statistics")
            
            # Create stats table
            stats_data = {
                'Metric': ['Total MNUs', 'Mean MNIS', 'Std MNIS', 'Min MNIS', 'Max MNIS',
                          'Excellent', 'Good', 'Moderate', 'Critical', 'Collapse'],
                'Value': [
                    selected_site['mnus'],
                    f"{avg_mnis:.3f}",
                    f"{0.15:.3f}",
                    f"{0.21:.3f}",
                    f"{0.78:.3f}",
                    '12%',
                    '38%',
                    '32%',
                    '14%',
                    '4%'
                ]
            }
            
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True, hide_index=True)
            
            # Recent alerts
            st.subheader("⚠️ Recent Alerts")
            alerts_data = {
                'Date': ['2026-02-25', '2026-02-20', '2026-02-15'],
                'Type': ['ρ_e decline', 'SER imbalance', 'K_topo reduction'],
                'Severity': ['High', 'Medium', 'Low']
            }
            df_alerts = pd.DataFrame(alerts_data)
            st.dataframe(df_alerts, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Map view
        st.subheader("🗺️ Site Locations")
        
        # Create sample map
        site_data = pd.DataFrame([
            {'lat': 52.7333, 'lon': 23.8667, 'name': 'Białowieża', 'mnis': 0.19},
            {'lat': 44.1167, 'lon': -118.6167, 'name': 'Oregon', 'mnis': 0.31},
            {'lat': -3.4653, 'lon': -62.2159, 'name': 'Amazon', 'mnis': 0.47},
            {'lat': 57.0, 'lon': -4.5, 'name': 'Caledonian', 'mnis': 0.63},
            {'lat': 46.5, 'lon': -81.0, 'name': 'Sudbury', 'mnis': 0.58},
        ])
        
        fig = px.scatter_mapbox(
            site_data,
            lat='lat',
            lon='lon',
            hover_name='name',
            color='mnis',
            color_continuous_scale=['green', 'yellow', 'red'],
            range_color=[0, 1],
            zoom=2,
            height=500
        )
        
        fig.update_layout(mapbox_style='open-street-map')
        fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.markdown("🍄 *The forest speaks. FUNGI-MYCEL translates.*")
        st.caption(f"FUNGI-MYCEL v1.0.0 | DOI: 10.14293/FUNGI-MYCEL.2026.001")
    
    def create_dash_app(self):
        """Create Dash dashboard app."""
        # This would be implemented for Dash backend
        raise NotImplementedError("Dash version coming soon")
    
    def run_streamlit(self):
        """Run Streamlit dashboard."""
        self.create_streamlit_app()


# Convenience functions
def create_dashboard_app(backend: str = 'streamlit'):
    """Create dashboard app with specified backend."""
    dashboard = MNISDashboard()
    
    if backend == 'streamlit':
        return dashboard.create_streamlit_app()
    elif backend == 'dash':
        return dashboard.create_dash_app()
    else:
        raise ValueError(f"Unknown backend: {backend}")


def run_dashboard(backend: str = 'streamlit', port: int = 8501):
    """
    Run the interactive dashboard.
    
    Args:
        backend: 'streamlit' or 'dash'
        port: Port to run on
    """
    if backend == 'streamlit':
        if not STREAMLIT_AVAILABLE:
            raise ImportError("streamlit is required")
        
        # This would typically be run with: streamlit run this_file.py
        dashboard = MNISDashboard()
        dashboard.run_streamlit()
    
    elif backend == 'dash':
        # Placeholder for Dash implementation
        print("Dash backend coming soon")
    
    else:
        raise ValueError(f"Unknown backend: {backend}")
