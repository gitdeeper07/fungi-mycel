# 🍄 FUNGI-MYCEL Dockerfile
# Mycelial Network Intelligence Framework
# Version: 1.0.0
# Base Image: Python 3.10 slim

FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /build

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    libpq-dev \
    libhdf5-dev \
    libnetcdf-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .
COPY setup.cfg .
COPY setup.py .
COPY MANIFEST.in .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --prefix=/install --no-deps -r requirements.txt && \
    pip install --prefix=/install --no-deps .

# -----------------------------------------------------------------------------
# Runtime stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FUNGI_MYCEL_HOME=/opt/fungi-mycel \
    FUNGI_MYCEL_CONFIG=/etc/fungi-mycel/config.yaml \
    FUNGI_MYCEL_DATA=/var/lib/fungi-mycel/data \
    FUNGI_MYCEL_LOGS=/var/log/fungi-mycel \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Set working directory
WORKDIR /opt/fungi-mycel

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # System utilities
    curl \
    wget \
    git \
    vim-tiny \
    procps \
    htop \
    # Database clients
    postgresql-client \
    redis-tools \
    # Scientific libraries
    libhdf5-103-1 \
    libnetcdf19 \
    libgdal30 \
    libgeos-c1v5 \
    libproj25 \
    libblas3 \
    liblapack3 \
    libatlas3-base \
    libffi8 \
    libssl3 \
    # Field hardware support
    libusb-1.0-0 \
    libserialport0 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories and user
RUN groupadd -r fungi && \
    useradd -r -g fungi -m -d /home/fungi -s /bin/bash fungi && \
    mkdir -p /etc/fungi-mycel && \
    mkdir -p /var/lib/fungi-mycel/data && \
    mkdir -p /var/lib/fungi-mycel/recordings && \
    mkdir -p /var/lib/fungi-mycel/backups && \
    mkdir -p /var/log/fungi-mycel && \
    mkdir -p /opt/fungi-mycel && \
    chown -R fungi:fungi /etc/fungi-mycel && \
    chown -R fungi:fungi /var/lib/fungi-mycel && \
    chown -R fungi:fungi /var/log/fungi-mycel && \
    chown -R fungi:fungi /opt/fungi-mycel

# Copy installed Python packages from builder
COPY --from=builder --chown=fungi:fungi /install /usr/local

# Copy application code
COPY --chown=fungi:fungi . /opt/fungi-mycel/

# Copy default configuration
COPY --chown=fungi:fungi config/fungi_mycel.docker.yaml /etc/fungi-mycel/config.yaml

# Install the package in development mode (for entrypoints)
RUN pip install -e /opt/fungi-mycel

# Switch to non-root user
USER fungi

# Expose ports
EXPOSE 8000 8501 9090

# Create volumes
VOLUME ["/etc/fungi-mycel", "/var/lib/fungi-mycel/data", "/var/lib/fungi-mycel/recordings", "/var/log/fungi-mycel"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import fungi_mycel; print('🍄 FUNGI-MYCEL healthy')" || exit 1

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/fungi-mycel"]

# Default command
CMD ["serve", "--all", "--host", "0.0.0.0"]

# -----------------------------------------------------------------------------
# Multi-stage build for different targets

# Development target
FROM builder AS development
WORKDIR /opt/fungi-mycel
COPY --from=builder /install /usr/local
COPY . .
RUN pip install -e ".[dev,ml,viz,geo,db,field,web,jupyter]"
CMD ["/bin/bash"]

# ML target (with GPU support)
FROM python:3.10 AS ml
RUN pip install tensorflow torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
COPY --from=builder /install /usr/local
COPY . /opt/fungi-mycel
WORKDIR /opt/fungi-mycel
CMD ["fungi-mycel", "serve", "--api"]

# Minimal target (for edge devices)
FROM python:3.10-slim AS minimal
COPY --from=builder /install /usr/local
COPY fungi_mycel /opt/fungi-mycel/fungi_mycel
COPY scripts /opt/fungi-mycel/scripts
WORKDIR /opt/fungi-mycel
CMD ["fungi-mycel", "--help"]

# -----------------------------------------------------------------------------
# Labels
LABEL maintainer="Samir Baladi <gitdeeper@gmail.com>"
LABEL version="1.0.0"
LABEL description="FUNGI-MYCEL - Mycelial Network Intelligence Framework"
LABEL org.opencontainers.image.source="https://gitlab.com/gitdeeper07/fungi-mycel"
LABEL org.opencontainers.image.documentation="https://fungi-mycel.readthedocs.io"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="FUNGI-MYCEL"
LABEL org.opencontainers.image.description="Quantitative Framework for Decoding Mycelial Network Intelligence"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2026-02-27"
LABEL org.opencontainers.image.url="https://fungi-mycel.netlify.app"
LABEL org.opencontainers.image.vendor="Ronin Institute"
LABEL org.opencontainers.image.authors="Samir Baladi"

# -----------------------------------------------------------------------------
# Build instructions:
#   docker build -t fungi-mycel:latest .
#   docker build --target development -t fungi-mycel:dev .
#   docker build --target ml -t fungi-mycel:ml .
#   docker build --target minimal -t fungi-mycel:minimal .
#
# Run:
#   docker run -p 8501:8501 fungi-mycel:latest
#   docker run -v /host/data:/var/lib/fungi-mycel/data fungi-mycel:latest process --input /data
