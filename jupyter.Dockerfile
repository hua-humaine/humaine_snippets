FROM kubeflownotebookswg/jupyter-scipy


RUN usermod -u 1000 jovyan
RUN usermod -d /home/jovyan jovyan


ENV NB_USER jovyan
ENV NB_UID 1000
ENV NB_PREFIX /
ENV HOME /home/$NB_USER
ENV SHELL /bin/bash

RUN chown -R jovyan /home/jovyan
USER jovyan



COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
