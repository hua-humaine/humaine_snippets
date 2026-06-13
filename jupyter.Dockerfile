# 1. Base image
FROM python:3.11-slim

# Installing tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Creation of user jovyan with UID 1000
RUN groupadd -g 1000 jovyan && \
    useradd -u 1000 -g jovyan -m -d /home/jovyan -s /bin/bash jovyan

# 3. Working directory
WORKDIR /home/jovyan

# 4.Installing dependencies with PIP
COPY --chown=jovyan:jovyan requirements.txt.locked .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt.locked

# 5. Copying sources with right permissions
COPY --chown=jovyan:jovyan scripts/ ./scripts/
COPY --chown=jovyan:jovyan notebook_snippets/ ./notebook_snippets/
COPY --chown=jovyan:jovyan pipelines/ ./pipelines/
COPY --chown=jovyan:jovyan src/ ./src/

# 6. Switch to jovyan
USER jovyan
