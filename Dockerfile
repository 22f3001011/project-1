FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-venv \
    git \
    curl \ 
    wget \
    sqlite3 \
    ffmpeg \
    imagemagick \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && \
    apt-get install -y nodejs && \
    node -v && \
    npm install -g prettier@3.4.2

# Upgrade pip and install packages in system python
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3 -m pip install --no-cache-dir \
    numpy \
    fastapi \
    uvicorn[standard] \
    requests \
    httpx \
    aiohttp \
    websockets \
    pandas \
    scipy \
    scikit-learn \
    duckdb \
    pyarrow \
    beautifulsoup4 \
    markdown \
    pyyaml \
    pytest \
    python-dotenv \
    seaborn \
    jupyter \
    notebook \
    jupyterlab \
    flask \
    django \
    requests \
    lxml \
    sqlalchemy \
    psycopg2-binary \
    python-dateutil \
    docstring-parser \
    pydantic \
    pillow

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /usr/local/bin/

# Create and set workdir
WORKDIR /app

# Create data directory
RUN mkdir -p /data

# Copy application files
COPY function_tasks.py .
COPY main.py .
COPY .env .

# Environment variables with defaults
ENV PIP_ROOT_USER_ACTION=ignore
ARG OPEN_AI_PROXY_URL=http://aiproxy.sanand.workers.dev/openai/v1/chat/completions
ARG OPEN_AI_EMBEDDING_URL=http://aiproxy.sanand.workers.dev/openai/v1/embeddings
ARG OPEN_AI_PROXY_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDEwMTFAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.LkE-L3x00t6esnJCRIanP6IFr2TAcqm6kj8-opeKxng

ENV OPEN_AI_PROXY_URL=$OPEN_AI_PROXY_URL
ENV OPEN_AI_EMBEDDING_URL=$OPEN_AI_EMBEDDING_URL
ENV OPEN_AI_PROXY_TOKEN=$OPEN_AI_PROXY_TOKEN

# Expose port
EXPOSE 8000

# Set the entrypoint
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]