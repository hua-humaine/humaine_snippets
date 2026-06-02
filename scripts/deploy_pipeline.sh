#!/bin/bash
set -e

echo "Detecting changed pipelines..."
PIPELINES_TO_RUN=$(python scripts/find_pipelines.py $CHANGED_FILES)

if [ -z "$PIPELINES_TO_RUN" ]; then
    echo "No pipeline changes detected."
    exit 0
fi

for FILE in $PIPELINES_TO_RUN; do
    echo "Processing changed pipeline: $FILE"
    
    # 1. Κάνουμε export το image ώστε να το "δει" το Python script (os.environ.get)
    export IMAGE_URL="$IMAGE_URL"
    
    # 2. Compile: Ο compiler πλέον θα φτιάξει το YAML ΜΕ ΤΟ ΣΩΣΤΟ IMAGE κατευθείαν!
    python $FILE
    echo "Successfully compiled YAML natively with image $IMAGE_URL"
    
    # 3. Dynamic Name Extraction (Αυτό το κρατάμε για να ξέρουμε ποιο pipeline να κάνουμε update)
    PIPELINE_NAME=$(python -c "import yaml; print(yaml.safe_load(open('pipeline_temp.yaml'))['pipelineInfo']['name'])")
    echo "Detected pipeline name from YAML: $PIPELINE_NAME"
    
    # 4. Submit: Στέλνουμε στο Kubeflow
    echo "Submitting pipeline as: $PIPELINE_NAME"
    python scripts/submit_to_kubeflow.py  \
        --file pipeline_temp.yaml \
        --url "$KUBEFLOW_URL" \
        --image "$IMAGE_URL" \
        --username "$KUBEFLOW_USERNAME" \
        --password "$KUBEFLOW_PASSWORD" \
        --pipeline-name "$PIPELINE_NAME" \
        --namespace "kubeflow-user-example-com"  # TODO: Dynamically get user namespace
        
    # 5. Καθαρισμός
    rm -f pipeline_temp.yaml
    echo "Finished processing $FILE"
done