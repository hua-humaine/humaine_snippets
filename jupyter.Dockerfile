FROM kubeflownotebookswg/jupyter-scipy

# 1. Ρυθμίσεις χρηστών (ως root)
USER root
RUN usermod -u 1000 jovyan && \
    usermod -d /home/jovyan jovyan

ENV NB_USER=jovyan
ENV NB_UID=1000
ENV NB_PREFIX=/
ENV HOME=/home/$NB_USER
ENV SHELL=/bin/bash

RUN chown -R jovyan /home/jovyan

# 2. Εγκατάσταση συστημικών εργαλείων ως root
# Προσθήκη --no-install-recommends για ταχύτερο build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Μετά τις εγκαταστάσεις, γυρνάμε στον χρήστη jovyan
USER jovyan
WORKDIR /home/jovyan

# 4. Αναβάθμιση εργαλείων pip και εγκατάσταση python πακέτων
# Αυτό λύνει το "subprocess-exited-with-error" για πακέτα όπως το xgboost
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY --chown=jovyan:jovyan requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt