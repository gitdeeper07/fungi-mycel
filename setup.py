#!/usr/bin/env python3
"""FUNGI-MYCEL: Mycelial Network Intelligence Framework.

A quantitative framework for decoding mycelial network intelligence,
bioelectrical communication, and sub-surface ecological sovereignty.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fungi-mycel",
    version="1.0.0",
    author="Samir Baladi",
    author_email="gitdeeper@gmail.com",
    description="FUNGI-MYCEL: Quantitative Framework for Mycelial Network Intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gitdeeper07/fungi-mycel",
    project_urls={
        "Bug Tracker": "https://gitlab.com/gitdeeper07/fungi-mycel/-/issues",
        "Documentation": "https://fungi-mycel.readthedocs.io",
        "Dashboard": "https://fungi-mycel.netlify.app",
        "DOI": "https://doi.org/10.14293/FUNGI-MYCEL.2026.001",
        "Source Code": "https://gitlab.com/gitdeeper07/fungi-mycel",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Ecology",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "scikit-learn>=1.0.0",
        "pyyaml>=5.4.0",
        "click>=8.0.0",
    ],
    extras_require={
        "ml": [
            "tensorflow>=2.8.0",
            "torch>=1.10.0",
            "xgboost>=1.6.0",
        ],
        "viz": [
            "seaborn>=0.11.0",
            "plotly>=5.5.0",
        ],
        "io": [
            "h5py>=3.6.0",
            "netCDF4>=1.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "ruff>=0.0.260",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "all": [
            "tensorflow>=2.8.0",
            "torch>=1.10.0",
            "xgboost>=1.6.0",
            "seaborn>=0.11.0",
            "plotly>=5.5.0",
            "h5py>=3.6.0",
            "netCDF4>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fungi-mycel = fungi_mycel.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
