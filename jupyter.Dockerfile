# Base image από το Kubeflow
FROM kubeflownotebookswg/jupyter-scipy

# 1. Ρυθμίσεις χρηστών ως root (απαραίτητο για εγκαταστάσεις)
USER root
RUN usermod -u 1000 jovyan && \
    usermod -d /home/jovyan jovyan

# Ρυθμίσεις περιβάλλοντος
ENV NB_USER=jovyan
ENV NB_UID=1000
ENV NB_PREFIX=/
ENV HOME=/home/$NB_USER
ENV SHELL=/bin/bash

RUN chown -R jovyan /home/jovyan

# 2. Εγκατάσταση συστημικών εργαλείων
# Χρησιμοποιούμε --no-install-recommends για εξοικονόμηση χώρου
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Προετοιμασία περιβάλλοντος για τον χρήστη jovyan
USER jovyan
WORKDIR /home/jovyan

# 4. Αναβάθμιση pip και εγκατάσταση από το requirements.txt
# Χρήση --only-binary=:all: για να αποφύγουμε τα compile errors (C++ errors)
# Το pip θα χρησιμοποιήσει το requirements.txt ως μοναδική πηγή (SSOT)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# Τελικό user setting για ασφάλεια
USER jovyan