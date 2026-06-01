import argparse
import os
from kfp import Client
sys.path.append(os.path.abspath("notebook_snippets"))
from KubeflowPipelineAPIConnector_New_version_cleaned import KFPCLientManager 

def submit_pipeline(file_name, url, image, username, password):
    kfp_client_manager = KFPCLientManager(
        host=url,
        dex_auth_type="local",
        dex_username=username,
        dex_password=password,
        skip_tls_verify=True
    )
    # Αν το pipeline υποστηρίζει ορίσματα
    # Tο image_url εδώ για να αντικατασταθεί δυναμικά.
    kfp_client_manager.create_run_from_pipeline_package()
        # pipeline_file=file_name,
        # arguments={
        #     "container_image": image # Αυτό πρέπει να είναι το όνομα του argument στο @dsl.pipeline σου
        # }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    submit_pipeline(args.file, args.url, args.image, args.username, args.password)