import requests
import kfp
import sys
import os
import subprocess

# Ρυθμίσεις
HOST = 'domain'
USERNAME = "user@example.com"
PASSWORD = "1234567890"
NAMESPACE = "kubeflow-user-example-com"

def run_compiler(script_path):
    print(f"Εκτέλεση του {script_path} για παραγωγή του YAML...")
    try:
        # Εκτελούμε το script ως ανεξάρτητη διεργασία
        subprocess.run([sys.executable, script_path], check=True)
        print("Compilation completed.")
    except subprocess.CalledProcessError as e:
        print(f"Σφάλμα κατά το compilation: {e}")
        sys.exit(1)

def get_authenticated_client():
    session = requests.Session()
    try:
        response = session.get(HOST)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"login": USERNAME, "password": PASSWORD}
        session.post(response.url, headers=headers, data=data)
        
        if "authservice_session" not in session.cookies:
            print("Error: Αποτυχία Authentication.")
            sys.exit(1)
            
        session_cookie = session.cookies.get_dict()["authservice_session"]
        
        return kfp.Client(
            host=f"{HOST}/pipeline",
            cookies=f"authservice_session={session_cookie}",
            namespace=NAMESPACE,
        )
    except Exception as e:
        print(f"Σφάλμα σύνδεσης: {e}")
        sys.exit(1)

def manage_pipelines(client, pipeline_name, yaml_path):
    print(f"Συνδεθήκαμε στο namespace: {client.get_user_namespace()}")
    
    pipelines = client.list_pipelines(page_size=100)
    pipeline_id = None
    
    if pipelines.pipelines:
        for p in pipelines.pipelines:
            if p.name == pipeline_name:
                pipeline_id = p.id
    
    # KFP v2: Upsert logic
    if pipeline_id:
        print(f"Ενημέρωση υπάρχοντος pipeline (ID: {pipeline_id})...")
        client.upload_pipeline_version(
            pipeline_package_path=yaml_path,
            pipeline_version_name="v-updated",
            pipeline_id=pipeline_id
        )
        print("Επιτυχής ενημέρωση!")
    else:
        print("Δημιουργία νέου pipeline...")
        client.upload_pipeline(
            pipeline_package_path=yaml_path, 
            pipeline_name=pipeline_name
        )
        print("Επιτυχής δημιουργία!")

if __name__ == "__main__":
    # Το SCRIPT_PATH παραμένει στον φάκελο pipelines
    SCRIPT_PATH = os.path.join("pipelines", "example_pipeline.py")
    
    # Το YAML_PATH βρίσκεται πλέον στο root, όπως το παράγει ο compiler
    YAML_PATH = "pipeline_temp.yaml"
    
    if not os.path.exists(SCRIPT_PATH):
        print(f"Error: Δεν βρέθηκε το {SCRIPT_PATH}")
    else:
        # 1. Παραγωγή YAML
        run_compiler(SCRIPT_PATH)
        
        # 2. Upload στο Kubeflow
        if not os.path.exists(YAML_PATH):
            print(f"Error: Το αρχείο {YAML_PATH} δεν παράχθηκε επιτυχώς.")
        else:
            client = get_authenticated_client()
            # Χρησιμοποιούμε το όνομα 'generic-training-pipeline-entry' 
            # όπως ορίστηκε στο @dsl.pipeline(name=...) μέσα στο example_pipeline.py
            manage_pipelines(client, "generic-training-pipeline-entry", YAML_PATH)