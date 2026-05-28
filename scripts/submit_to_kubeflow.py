import argparse
import os
import kfp
from dotenv import load_dotenv

load_dotenv()

def submit(pipeline_file, image_tag):
    # Σύνδεση με Token
    client = kfp.Client(
        host=os.getenv("KUBEFLOW_URL"),
        existing_token=os.getenv("KUBEFLOW_TOKEN")
    )
    
    # Δυναμικό όνομα
    file_base = os.path.splitext(os.path.basename(pipeline_file))[0]
    pipeline_name = f"{file_base}-run-{os.getenv('GITHUB_RUN_NUMBER')}"
    
    print(f"Uploading {pipeline_name}...")
    client.upload_pipeline(
        pipeline_package_path=pipeline_file,
        pipeline_name=pipeline_name
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    submit(args.file, args.image)