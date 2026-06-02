# 1. Base image (Python 3.9)
FROM python:3.9-slim

# Εγκατάσταση απαραίτητων εργαλείων
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Δημιουργία του χρήστη jovyan με UID 1000
RUN groupadd -g 1000 jovyan && \
    useradd -u 1000 -g jovyan -m -d /home/jovyan -s /bin/bash jovyan

# 3. Ορισμός φακέλου εργασίας
WORKDIR /home/jovyan

# 4. Εγκατάσταση των dependencies με PIP
COPY --chown=jovyan:jovyan requirements.txt .
RUN  pip install --no-cache-dir -r requirements.txt

# 5. Αντιγραφή πηγών με τα σωστά permissions
COPY --chown=jovyan:jovyan scripts/ ./scripts/
COPY --chown=jovyan:jovyan notebook_snippets/ ./notebook_snippets/
COPY --chown=jovyan:jovyan pipelines/ ./pipelines/
COPY --chown=jovyan:jovyan src/ ./src/

# 6. Εναλλαγή στον χρήστη jovyan
USER jovyan