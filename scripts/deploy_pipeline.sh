#!/bin/bash
set -e

echo "Detecting changed pipelines..."
# Το git diff αφαιρέθηκε! Διαβάζουμε απευθείας τη μεταβλητή από το GitHub Actions
echo "Files to check: $CHANGED_FILES"

PIPELINES_TO_RUN=$(python scripts/find_pipelines.py $CHANGED_FILES)

if [ -z "$PIPELINES_TO_RUN" ]; then
    echo "No pipeline changes detected."
    exit 0
fi

for FILE in $PIPELINES_TO_RUN; do
    echo "Processing changed pipeline: $FILE"
    
    # 1. Compile: Παράγουμε το YAML
    python $FILE --output pipeline_temp.yaml
    
    # 2. Injection: Αντικαθιστούμε το image δυναμικά στο YAML 
    if command -v yq &> /dev/null; then
        yq -i "(.spec.templates[] | select(.container.image != null) | .container.image) = \"$IMAGE_URL\"" pipeline_temp.yaml
        echo "Successfully injected image $IMAGE_URL into YAML."
    else
        echo "yq not found, skipping image injection."
    fi
    
    # 3. Submit: Στέλνουμε στο Kubeflow
    python scripts/submit_to_kubeflow.py  \
        --file pipeline_temp.yaml \
        --url "$KUBEFLOW_URL" \
        --image "$IMAGE_URL" \
        --username "$KUBEFLOW_USERNAME" \
        --password "$KUBEFLOW_PASSWORD"
    
    # 4. Καθαρισμός
    rm -f pipeline_temp.yaml
    echo "Finished processing $FILE"
done