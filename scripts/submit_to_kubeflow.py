import argparse
import os
import sys
import kfp
from kfp_server_api.exceptions import ApiException

# Path setup
sys.path.append(os.path.abspath("notebook_snippets"))
from KubeflowPipelineAPIConnector_New_version_cleaned import KFPClientManager 

def get_client(url, username, password):
    """Factory function for KFP client creation."""
    manager = KFPClientManager(
        api_url=url,
        dex_username=username,
        dex_password=password,
        dex_auth_type="local",
        skip_tls_verify=True
    )
    return manager.create_kfp_client()

def submit_pipeline(file_name, url, image, username, password):
    print(f"DEBUG: KFP SDK {kfp.__version__} | Target: {url}")
    client = get_client(url, username, password)
    
    # Επιλογή στρατηγικής βάσει έκδοσης
    is_v2 = kfp.__version__.startswith("2.")
    
    try:
        if is_v2:
            print("Submitting via KFP v2 logic...")
            client.create_run_from_pipeline_package(
                pipeline_file=file_name,
                arguments={"container_image": image},
                experiment_name='Default'
            )
        else:
            print("Submitting via KFP v1 (Legacy) logic...")
            # Upload first to avoid complex package parsing in v1
            pipeline = client.upload_pipeline(pipeline_package_path=file_name)
            client.create_run_from_pipeline_id(
                pipeline_id=pipeline.id,
                experiment_name='Default',
                arguments={"container_image": image}
            )
        print("Pipeline submitted successfully.")
        
    except ApiException as e:
        print(f"API Error {e.status}: {e.reason}\nBody: {e.body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for arg in ["file", "image", "url", "username", "password"]:
        parser.add_argument(f"--{arg}", required=True)
    args = parser.parse_args()

    submit_pipeline(args.file, args.url, args.image, args.username, args.password)