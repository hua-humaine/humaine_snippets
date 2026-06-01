FROM kubeflownotebookswg/jupyter-scipy

# 1. Ρυθμίσεις χρηστών (ως root)
USER root
RUN usermod -u 1000 jovyan && \
    usermod -d /home/jovyan jovyan

ENV NB_USER jovyan
ENV NB_UID 1000
ENV NB_PREFIX /
ENV HOME /home/$NB_USER
ENV SHELL /bin/bash

RUN chown -R jovyan /home/jovyan

# 2. Εγκατάσταση συστημικών εργαλείων (ως root - ΕΔΩ ΗΤΑΝ ΤΟ ΛΑΘΟΣ)
# Πρέπει να τρέξει ως root, οπότε το αφήνουμε μετά το USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Μετά τις εγκαταστάσεις, γυρνάμε στον χρήστη jovyan
USER jovyan

# 4. Εγκατάσταση python πακέτων
COPY --chown=jovyan:jovyan requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt