import argparse
import os
import sys
import kfp
from kfp_server_api.exceptions import ApiException

# Προσθέτουμε το path για να βρει το module
sys.path.append(os.path.abspath("notebook_snippets"))
from KubeflowPipelineAPIConnector_New_version_cleaned import KFPClientManager 

def submit_pipeline(file_name, url, image, username, password):
    print(f"--- Environment Debug ---")
    print(f"KFP SDK Version: {kfp.__version__}")
    print(f"Target URL: {url}")
    print(f"--------------------------")

    manager = KFPClientManager(
        api_url=url,
        dex_username=username,
        dex_password=password,
        dex_auth_type="local",
        skip_tls_verify=True
    )
    
    print("Authenticating with Kubeflow...")
    client = manager.create_kfp_client()

    print(f"Submitting pipeline: {file_name} with image: {image}")
    
    try:
        # Ανίχνευση του API Version από τον client
        # Αν το cluster είναι παλιό, ο client συχνά εμφανίζει v1beta1 ή v1
        api_version = getattr(client, '_api_version', 'v2beta1')
        print(f"Detected API version: {api_version}")

        if "v2" in api_version:
            # V2 Logic (όπως το είχες)
            client.create_run_from_pipeline_package(
                pipeline_file=file_name,
                arguments={"container_image": image},
                experiment_name='Default'
            )
        else:
            # Legacy V1 Logic: Χρησιμοποιούμε το upload_pipeline και μετά create_run
            # Αυτό παρακάμπτει το endpoint /experiments που κρασάρει
            pipeline_upload = client.upload_pipeline(pipeline_package_path=file_name)
            client.create_run_from_pipeline_package(
                pipeline_id=pipeline_upload.id,
                arguments={"container_image": image},
                experiment_name='Default',
                run_name=f"run-{image.split(':')[-1]}"
            )
            
        print("Pipeline submitted successfully.")
        
    except ApiException as e:
        print(f"ApiException caught (Status: {e.status}): {e.reason}")
        print(f"Body: {e.body}")
        # Αν το 404 επιμένει, εδώ ξέρουμε σίγουρα ότι φταίει το endpoint
        sys.exit(1)
    except Exception as e:
        print(f"General error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    submit_pipeline(args.file, args.url, args.image, args.username, args.password)