import argparse
import os
import sys
import kfp
from kfp_server_api.exceptions import ApiException

# Προσθέτουμε το path για να βρει το module
sys.path.append(os.path.abspath("notebook_snippets"))
from KubeflowPipelineAPIConnector_New_version_cleaned import KFPClientManager 

def submit_pipeline(file_name, url, image, username, password):
    # Debugging: Εκτύπωση έκδοσης στο console του GitHub Actions
    print(f"--- Environment Debug ---")
    print(f"KFP SDK Version: {kfp.__version__}")
    print(f"Target URL: {url}")
    print(f"--------------------------")

    # 1. Αρχικοποίηση του Manager
    manager = KFPClientManager(
        api_url=url,
        dex_username=username,
        dex_password=password,
        dex_auth_type="local",
        skip_tls_verify=True
    )
    
    # 2. Σύνδεση
    print("Authenticating with Kubeflow...")
    client = manager.create_kfp_client()

    # 3. Υποβολή του pipeline με υβριδική λογική
    print(f"Submitting pipeline: {file_name} with image: {image}")
    
    try:
        # Έλεγχος αν τρέχουμε σε KFP SDK v2 (major version >= 2)
        major_version = int(kfp.__version__.split('.')[0])
        
        if major_version >= 2:
            # Υποβολή για KFP v2 (Απαιτεί experiment_name)
            client.create_run_from_pipeline_package(
                pipeline_file=file_name,
                arguments={"container_image": image},
                experiment_name='Default'
            )
        else:
            # Υποβολή για KFP v1 (Classic)
            client.create_run_from_pipeline_package(
                pipeline_file=file_name,
                arguments={"container_image": image}
            )
        print("Pipeline submitted successfully.")
        
    except ApiException as e:
        print(f"ApiException caught (Status: {e.status}): {e.reason}")
        print(f"Body: {e.body}")
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