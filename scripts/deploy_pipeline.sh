#!/bin/bash
set -e  # Σταματάει το script αν κάποια εντολή αποτύχει

echo "Detecting changed pipelines..."
CHANGED_FILES=$(git diff --name-only $PRE_COMMIT_SHA $SHA || git ls-files)
PIPELINES_TO_RUN=$(python scripts/find_pipelines.py $CHANGED_FILES)

if [ -z "$PIPELINES_TO_RUN" ]; then
    echo "No pipeline changes detected."
    exit 0
fi

for FILE in $PIPELINES_TO_RUN; do
    echo "Processing changed pipeline: $FILE"
    
    # Compile
    python $FILE --output pipeline_temp.yaml
    
    # Submit
    # python scripts/submit_to_kubeflow.py --file pipeline_temp.yaml --image "$IMAGE_URL"
    echo "Printing environment variables for debugging:"
    echo "KUBEFLOW_URL: $KUBEFLOW_URL"
    echo "IMAGE_URL: $IMAGE_URL"
    
    python sripts/submit_to_kubeflow.py  \
        --file pipeline_temp.yaml \
        --url "$KUBEFLOW_URL" \
        --image "$IMAGE_URL" \
        --username "$KUBEFLOW_USERNAME" \
        --password "$KUBEFLOW_PASSWORD"
    
    # Καθαρισμός
    rm pipeline_temp.yaml
done