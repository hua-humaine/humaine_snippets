from kfp import dsl

# Ορίζουμε ένα απλό base_image για να μην γκρινιάζει το Kubeflow. 
# Δεν μας νοιάζει ποιο είναι, γιατί το yq θα το κάνει override με το δικό σου!
@dsl.component(base_image='python:3.10')
def train_model_op():
    import pandas as pd
    from sklearn.datasets import make_classification
    # ... ο κώδικας σου ...
    print("Training component running..")

@dsl.pipeline(name='generic-training-pipeline-entry')
def my_pipeline(): 
    # Αφαιρέσαμε την παράμετρο image_tag. Το pipeline πλέον είναι καθαρό.
    train_task = train_model_op()
    
    # Το train_task.set_image() διαγράφηκε εντελώς!

if __name__ == "__main__":
    from kfp import compiler
    
    # Παράγουμε το YAML. Άλλαξα το όνομα σε pipeline_temp.yaml 
    # για να ταιριάζει ακριβώς με το bash script σου (deploy_pipeline.sh)
    compiler.Compiler().compile(
        pipeline_func=my_pipeline,
        package_path='pipeline_temp.yaml'
    )