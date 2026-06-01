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

# 2. Εγκατάσταση συστημικών εργαλείων
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Προετοιμασία περιβάλλοντος για τον χρήστη jovyan
USER jovyan
WORKDIR /home/jovyan

# 4. Αναβάθμιση εργαλείων pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 5. Εγκατάσταση σταθερών πακέτων από το αρχείο (cache layer)
COPY --chown=jovyan:jovyan requirements_stable.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements_stable.txt

# 6. Εγκατάσταση δυναμικών πακέτων hardcoded (upgrade mode)
# Εδώ θα βάζεις τα πακέτα που θέλεις να αναβαθμίζονται σε κάθε build
RUN pip install --no-cache-dir --upgrade --prefer-binary \
    shap \
    pycaret \
    xgboost \
    scikit-learn

# Τελικό user setting για ασφάλεια
USER jovyan