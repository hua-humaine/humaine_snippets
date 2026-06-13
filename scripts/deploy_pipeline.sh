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
    echo "Compiling pipeline via self-execution..."
    python3 "$TEMP_PY_FILE"
    
    # 3. Submit: Iterate through ANY .yaml file created in this directory
    GENERATED_YAMLs=$(ls *.yaml 2>/dev/null || true)
    
    if [ -z "$GENERATED_YAMLs" ]; then
        echo "Error: No YAML files were generated."
        exit 1
    fi

    for YAML_FILE in $GENERATED_YAMLs; do
        echo "Found pipeline artifact: $YAML_FILE"
        
        # Extract name dynamically
        PIPELINE_NAME=$(python -c "import yaml; print(yaml.safe_load(open('$YAML_FILE'))['pipelineInfo']['name'])")
        echo "Submitting $PIPELINE_NAME from $YAML_FILE..."
        
        # 4. Submit
        python scripts/submit_to_kubeflow.py \
            --file "$YAML_FILE" \
            --url "$KUBEFLOW_URL" \
            --username "$KUBEFLOW_USERNAME" \
            --password "$KUBEFLOW_PASSWORD" \
            --pipeline-name "$PIPELINE_NAME" \
            --image "$IMAGE_URL" \
            --namespace "kubeflow-user-example-com"
            
        # 5. Cleanup individual file
        rm -f "$YAML_FILE"
    done
    
    # Cleanup injection file
    rm -f "$TEMP_PY_FILE"

    echo "Finished processing $FILE"
    echo "-----------------------------------"
done