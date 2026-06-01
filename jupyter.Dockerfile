# Base image από το Kubeflow
FROM kubeflownotebookswg/jupyter-scipy

# 1. Ρυθμίσεις χρηστών (ως root)
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

# 2. Εγκατάσταση συστημικών εργαλείων (build-essential για C++ compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Προετοιμασία περιβάλλοντος για τον χρήστη jovyan
USER jovyan
WORKDIR /home/jovyan

# 4. Αναβάθμιση εργαλείων pip
# Αυτό τρέχει πρώτο για να έχουμε τα τελευταία εργαλεία εγκατάστασης
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 5. Αντιγραφή requirements.txt και εγκατάσταση πακέτων
# Το COPY πρέπει να προηγείται του pip install -r
COPY --chown=jovyan:jovyan requirements.txt .
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# Τελικό user setting για ασφάλεια
USER jovyan