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

# 2. Εγκατάσταση των dependencies
# Χρησιμοποιούμε --mount=type=cache για να μην ξανακατεβάζει τα πακέτα από το μηδέν
# Αφαιρέσαμε το --no-cache ώστε το uv να εκμεταλλεύεται τον τοπικό cache φάκελο
COPY --chown=jovyan:jovyan requirements.txt .
RUN --mount=type=cache,target=/home/jovyan/.cache/uv \
    uv pip install --system -r requirements.txt

# 3. Αντιγραφή πηγαίου κώδικα
# Αν αλλάξει κάποιο αρχείο στους παρακάτω φακέλους, το Docker θα ξανατρέξει 
# μόνο αυτά τα layers, διατηρώντας τα dependencies (Step 2) CACHED.
COPY --chown=jovyan:jovyan scripts/ ./scripts/
COPY --chown=jovyan:jovyan XAIsnippets/ ./XAIsnippets/
COPY --chown=jovyan:jovyan notebook_snippets/ ./notebook_snippets/

USER jovyan