# -------------------- 🔨 Build Stage --------------------
FROM python:3.11-slim AS build

# Environment setup to avoid __pycache__, buffer logs, and avoid pip cache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Copy only dependency files first for better Docker cache
COPY requirements.txt constraints.txt ./

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Add UV (blazing-fast package manager)
COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /uvx /bin/

# Install Python dependencies using UV with constraints
RUN uv pip install --system -r requirements.txt

# Now copy the entire project
COPY . .

# Run one-time script for population
RUN python populate.py


# -------------------- 🧼 Final Stage --------------------
FROM python:3.11-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Copy only installed packages and app code from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app /app

# Install system runtime libs (no dev tools now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Expose the port for your Flask + SocketIO backend
EXPOSE 5000

# Run the Flask-SocketIO app
CMD ["python", "main.py"]
