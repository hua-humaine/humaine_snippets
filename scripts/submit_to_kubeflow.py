import argparse
import os
import sys
import time
import requests
import kfp
from kfp_server_api.exceptions import ApiException

def get_authenticated_client(url, username, password, namespace):
    """Αυθεντικοποίηση μέσω Dex και δημιουργία KFP Client."""
    # Αφαιρούμε το / στο τέλος αν υπάρχει, για να χτίσουμε σωστά τα paths
    base_url = url.rstrip('/') 
    session = requests.Session()
    
    try:
        print(f"Authenticating to {base_url}...")
        response = session.get(base_url)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"login": username, "password": password}
        session.post(response.url, headers=headers, data=data)
        
        if "authservice_session" not in session.cookies:
            print("Error: Αποτυχία Authentication. Ελέγξτε τα credentials.")
            sys.exit(1)
            
        session_cookie = session.cookies.get_dict()["authservice_session"]
        print("Authentication successful!")
        
        # Δημιουργία και επιστροφή του Client για το KFP v2
        return kfp.Client(
            host=f"{base_url}/pipeline",
            cookies=f"authservice_session={session_cookie}",
            namespace=namespace,
        )
    except Exception as e:
        print(f"Σφάλμα σύνδεσης: {e}")
        sys.exit(1)

def submit_pipeline(file_name, url, image, username, password, namespace, pipeline_name):
    print(f"DEBUG: KFP SDK {kfp.__version__} | Target: {url}")
    
    if not os.path.exists(file_name):
        print(f"Error: Το αρχείο YAML '{file_name}' δεν βρέθηκε.")
        sys.exit(1)

    client = get_authenticated_client(url, username, password, namespace)
    
    try:
        # 1. UPSERT ΛΟΓΙΚΗ (Ανανέωση ή Δημιουργία του Pipeline Definition)
        print(f"\n--- Upserting Pipeline: {pipeline_name} ---")
        
        # Η get_pipeline_id είναι η πιο ασφαλής μέθοδος του KFP SDK
        pipeline_id = client.get_pipeline_id(pipeline_name)
        
        # Δημιουργούμε ένα δυναμικό όνομα έκδοσης (π.χ. v-171542123) 
        # για να αποφύγουμε version name conflicts στα συνεχόμενα CI/CD runs
        version_name = f"v-{int(time.time())}" 
        
        if pipeline_id:
            print(f"Βρέθηκε υπάρχον pipeline (ID: {pipeline_id}). Uploading νέας έκδοσης ({version_name})...")
            client.upload_pipeline_version(
                pipeline_package_path=file_name,
                pipeline_version_name=version_name,
                pipeline_id=pipeline_id
            )
        else:
            print(f"Δεν βρέθηκε το pipeline. Δημιουργία νέου: {pipeline_name}...")
            client.upload_pipeline(
                pipeline_package_path=file_name, 
                pipeline_name=pipeline_name
            )

        # 2. RUN ΛΟΓΙΚΗ (Εκτέλεση του Pipeline)
        print(f"\n--- Submitting Run ---")
        client.create_run_from_pipeline_package(
            pipeline_file=file_name,
            arguments={"container_image": image} if image else {},
            experiment_name='Default',
            pipeline_name=pipeline_name
        )
        print("Pipeline run submitted successfully!")

    except ApiException as e:
        print(f"API Error {e.status}: {e.reason}\nBody: {e.body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload and Submit KFP Pipeline")
    
    # Απαραίτητες παράμετροι
    parser.add_argument("--file", required=True, help="Path to the compiled YAML file")
    parser.add_argument("--url", required=True, help="Base URL of Kubeflow")
    parser.add_argument("--username", required=True, help="Dex Username")
    parser.add_argument("--password", required=True, help="Dex Password")
    
    # Νέες απαραίτητες παράμετροι για το cluster σου
    parser.add_argument("--namespace", required=True, help="The Kubeflow user namespace")
    parser.add_argument("--pipeline-name", required=True, help="Name of the pipeline in UI")
    
    # Προαιρετική παράμετρος (αν το pipeline σου δεν παίρνει image ως input, δεν θα "σκάσει")
    parser.add_argument("--image", required=False, help="Container image tag (optional)")
    
    args = parser.parse_args()

    submit_pipeline(
        file_name=args.file, 
        url=args.url, 
        image=args.image, 
        username=args.username, 
        password=args.password,
        namespace=args.namespace,
        pipeline_name=args.pipeline_name
    )