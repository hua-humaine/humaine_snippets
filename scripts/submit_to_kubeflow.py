import argparse
import os
import sys

# Προσθέτουμε το path για να βρει το module
sys.path.append(os.path.abspath("notebook_snippets"))
from KubeflowPipelineAPIConnector_New_version_cleaned import KFPClientManager 

def submit_pipeline(file_name, url, image, username, password):
    # 1. Αρχικοποίηση του Manager
    manager = KFPClientManager(
        api_url=url,
        dex_username=username,
        dex_password=password,
        dex_auth_type="local",
        skip_tls_verify=True
    )
    
    # 2. Σύνδεση και λήψη του authenticated client
    print("Authenticating with Kubeflow...")
    client = manager.create_kfp_client()

    # 3. Υποβολή του pipeline
    print(f"Submitting pipeline: {file_name} with image: {image}")
    client.create_run_from_pipeline_package(
        pipeline_file=file_name,
        arguments={
            "container_image": image  # Αυτό αντιστοιχεί στο όνομα του argument στο @dsl.pipeline
        }
    )
    print("Pipeline submitted successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    submit_pipeline(args.file, args.url, args.image, args.username, args.password)