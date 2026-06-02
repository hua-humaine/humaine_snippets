import argparse
import os
import sys
import time
import requests
import kfp
from kfp_server_api.exceptions import ApiException

def get_authenticated_client(url, username, password, namespace):
    """Authenticate via Dex and create a KFP Client instance."""
    # Remove trailing slash if present to properly construct URL paths
    base_url = url.rstrip('/') 
    session = requests.Session()
    
    try:
        print(f"Authenticating to {base_url}...")
        response = session.get(base_url)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"login": username, "password": password}
        session.post(response.url, headers=headers, data=data)
        
        if "authservice_session" not in session.cookies:
            print("Error: Authentication failed. Please check your credentials.")
            sys.exit(1)
            
        session_cookie = session.cookies.get_dict()["authservice_session"]
        print("Authentication successful!")
        
        return kfp.Client(
            host=f"{base_url}/pipeline",
            cookies=f"authservice_session={session_cookie}",
            namespace=namespace,
        )
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

def submit_pipeline(file_name, url, username, password, namespace, pipeline_name):
    print(f"DEBUG: KFP SDK {kfp.__version__} | Target: {url}")
    
    if not os.path.exists(file_name):
        print(f"Error: Compiled YAML file '{file_name}' not found.")
        sys.exit(1)

    client = get_authenticated_client(url, username, password, namespace)
    
    try:
        # UPSERT LOGIC: Update existing or create a new pipeline definition
        print(f"\n--- Upserting Pipeline: {pipeline_name} ---")
        
        # Safely retrieve the pipeline ID if it already exists
        pipeline_id = client.get_pipeline_id(pipeline_name)
        
        # Generate a dynamic version name (e.g., v-171542123) to avoid conflicts on subsequent CI/CD runs
        version_name = f"v-{int(time.time())}" 
        
        if pipeline_id:
            print(f"Found existing pipeline (ID: {pipeline_id}). Uploading new version ({version_name})...")
            client.upload_pipeline_version(
                pipeline_package_path=file_name,
                pipeline_version_name=version_name,
                pipeline_id=pipeline_id
            )
        else:
            print(f"Pipeline not found. Creating new pipeline: {pipeline_name}...")
            client.upload_pipeline(
                pipeline_package_path=file_name, 
                pipeline_name=pipeline_name
            )

        print(f"Success! Pipeline YAML uploaded to the cluster. (Auto-run is disabled)")

    except ApiException as e:
        print(f"API Error {e.status}: {e.reason}\nBody: {e.body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload and Submit KFP Pipeline")
    
    # Required arguments
    parser.add_argument("--file", required=True, help="Path to the compiled YAML file")
    parser.add_argument("--url", required=True, help="Base URL of Kubeflow")
    parser.add_argument("--username", required=True, help="Dex Username")
    parser.add_argument("--password", required=True, help="Dex Password")
    parser.add_argument("--namespace", required=True, help="The Kubeflow user namespace")
    parser.add_argument("--pipeline-name", required=True, help="Name of the pipeline in UI")
    
    # Kept to ensure compatibility with deploy_pipeline.sh arguments, unused in Python
    parser.add_argument("--image", required=False, help="Container image tag (optional, currently unused)")
    
    args = parser.parse_args()

    submit_pipeline(
        file_name=args.file, 
        url=args.url, 
        username=args.username, 
        password=args.password,
        namespace=args.namespace,
        pipeline_name=args.pipeline_name
    )