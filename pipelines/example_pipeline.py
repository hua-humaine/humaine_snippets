import os
from kfp import dsl

# ΔΥΝΑΜΙΚΟ IMAGE: Διαβάζει από το CI/CD. 
# Αν το τρέξεις τοπικά, χρησιμοποιεί το 'python:3.10'.
# TODO: Ξεκαθάρισμα στους devs για το image που θελουν 
TARGET_IMAGE = os.environ.get("IMAGE_URL", "python:3.10")

@dsl.component(base_image=TARGET_IMAGE)
def train_model_op():
    import pandas as pd
    from sklearn.datasets import make_classification
    # ... ο κώδικας σου ...
    print("Training component running....")

@dsl.pipeline(name='generic-training-pipeline-entry')
def my_pipeline(): 
    train_task = train_model_op()

if __name__ == "__main__":
    from kfp import compiler
    import sys
    
    # Παράγουμε το YAML. 
    compiler.Compiler().compile(
        pipeline_func=my_pipeline,
        package_path='pipeline_temp.yaml'
    )