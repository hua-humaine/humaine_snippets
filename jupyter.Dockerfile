# Base image
FROM kubeflownotebookswg/jupyter-scipy

# 1. Εγκατάσταση του uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv /bin/

USER root
RUN usermod -u 1000 jovyan && usermod -d /home/jovyan jovyan
ENV NB_USER=jovyan
ENV HOME=/home/jovyan
RUN chown -R jovyan /home/jovyan

USER jovyan
WORKDIR /home/jovyan

# 2. Εγκατάσταση των dependencies (Αυτό θα παραμένει CACHED)
COPY --chown=jovyan:jovyan requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

# 3. Αντιγραφή μόνο των απαραίτητων πηγών (Αυτό είναι το "έξυπνο" COPY)
# Αντιγράφουμε κάθε φάκελο ξεχωριστά. Αν αλλάξεις κάτι μέσα στο XAIsnippets,
# το Docker θα ξανατρέξει μόνο αυτό το layer, αλλά θα κρατήσει το cache των dependencies!
COPY --chown=jovyan:jovyan scripts/ ./scripts/
COPY --chown=jovyan:jovyan notebook_snippets/ ./notebook_snippets/

USER jovyan