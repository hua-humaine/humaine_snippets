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
    
    # 1. Image Injection: Creation of temporary Python file with the injected image
    TEMP_PY_FILE="${FILE}_temp_injected.py"
    echo "Injecting image $IMAGE_URL into Python AST (respecting humaineImage flag)..."
    python scripts/inject_image.py "$FILE" "$TEMP_PY_FILE" "$IMAGE_URL"
    
    # 2. Compile: Execute the pipeline file directly.
    # The file itself contains the logic to compile to 'pipeline_temp.yaml'
    echo "Compiling pipeline via self-execution..."
    python3 "$TEMP_PY_FILE"
    
    if [ ! -f "pipeline_temp.yaml" ]; then
        echo "Error: Compilation failed. pipeline_temp.yaml was not generated."
        exit 1
    fi

    echo "Successfully generated pipeline_temp.yaml"
    
    # 3. Dynamic Name Extraction: We read the pipeline name from the generated YAML
    PIPELINE_NAME=$(python -c "import yaml; print(yaml.safe_load(open('pipeline_temp.yaml'))['pipelineInfo']['name'])")
    echo "Detected pipeline name from YAML: $PIPELINE_NAME"
    
    # 4. Submit: We submit the YAML to Kubeflow
    echo "Submitting pipeline as: $PIPELINE_NAME"
    python scripts/submit_to_kubeflow.py  \
        --file pipeline_temp.yaml \
        --url "$KUBEFLOW_URL" \
        --username "$KUBEFLOW_USERNAME" \
        --password "$KUBEFLOW_PASSWORD" \
        --pipeline-name "$PIPELINE_NAME" \
        --image "$IMAGE_URL" \
        --namespace "kubeflow-user-example-com" # TODO: DYNAMIC USER NAMESPACE
        
    # 5. Cleanup: We remove the temporary files to keep the environment clean
    rm -f pipeline_temp.yaml
    rm -f "$TEMP_PY_FILE"
    
    echo "Finished processing $FILE"
    echo "-----------------------------------"
done