#!/bin/bash
set -e

echo "Detecting changed pipelines..."
echo "Files to check: $CHANGED_FILES"

# Βρίσκουμε ποια αρχεία άλλαξαν
PIPELINES_TO_RUN=$(python scripts/find_pipelines.py $CHANGED_FILES)

if [ -z "$PIPELINES_TO_RUN" ]; then
    echo "No pipeline changes detected."
    exit 0
fi

for FILE in $PIPELINES_TO_RUN; do
    echo "Processing changed pipeline: $FILE"
    
    # 1. Compile: Παράγουμε το YAML
    # Υποθέτουμε ότι το script δέχεται το όρισμα --output
    python $FILE --output pipeline_temp.yaml
    
    # 2. Injection: Αντικαθιστούμε το image δυναμικά στο YAML 
    if command -v yq &> /dev/null; then
        yq -i "(.spec.templates[] | select(.container.image != null) | .container.image) = \"$IMAGE_URL\"" pipeline_temp.yaml
        echo "Successfully injected image $IMAGE_URL into YAML."
        
        # 3. Dynamic Name Extraction: Παίρνουμε το όνομα από το YAML
        # Αυτό εξασφαλίζει ότι το script 'παντρεύεται' με το pipeline στο cluster
        PIPELINE_NAME=$(yq '.pipelineInfo.name' pipeline_temp.yaml)
        echo "Detected pipeline name from YAML: $PIPELINE_NAME"
    else
        echo "yq not found, skipping image injection and auto-name detection."
        # Fallback αν δεν υπάρχει yq
        PIPELINE_NAME=$(basename "$FILE" .py)
    fi
    
    # 4. Submit: Στέλνουμε στο Kubeflow μέσω του APIConnector σου
    echo "Submitting pipeline to Kubeflow..."
    python scripts/submit_to_kubeflow.py  \
        --file pipeline_temp.yaml \
        --url "$KUBEFLOW_URL" \
        --image "$IMAGE_URL" \
        --username "$KUBEFLOW_USERNAME" \
        --password "$KUBEFLOW_PASSWORD" \
        --pipeline-name "$PIPELINE_NAME" \
        --namespace "kubeflow-user-example-com"  // TODO: Get namespace dynamically
    
    # 5. Καθαρισμός
    rm -f pipeline_temp.yaml
    echo "Finished processing $FILE"
done