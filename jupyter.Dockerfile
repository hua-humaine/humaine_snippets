# Base image
FROM kubeflownotebookswg/jupyter-scipy

# 1. Εγκατάσταση του uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv /bin/

USER root
RUN usermod -u 1000 jovyan && usermod -d /home/jovyan jovyan
ENV NB_USER=jovyan
RUN chown -R jovyan /home/jovyan

USER jovyan
WORKDIR /home/jovyan

# 2. Εγκατάσταση των dependencies με το uv
# Το uv pip install είναι 10-100x πιο γρήγορο και έχει τον καλύτερο solver
COPY --chown=jovyan:jovyan requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

# Τελικό user setting για ασφάλεια
USER jovyan