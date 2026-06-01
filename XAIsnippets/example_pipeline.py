from kfp import dsl

@dsl.component
def train_model_op():
    import pandas as pd
    from sklearn.datasets import make_classification
    # ... ο κώδικας σου ...
    print("Training component running......")

@dsl.pipeline(name='generic-training-pipeline')
def my_pipeline(image_tag: str): # <--- Περνάμε το image ως παράμετρο
    # Χρησιμοποιούμε το container_spec για να ορίσουμε το image δυναμικά
    train_task = train_model_op()
    train_task.set_image(image_tag) 

if __name__ == "__main__":
    from kfp import compiler
    # Κατά το compile, δεν μας νοιάζει το image, 
    # θα το δώσουμε στο Kubeflow την ώρα του submission!
    compiler.Compiler().compile(
        pipeline_func=my_pipeline,
        package_path='pipeline.yaml'
    )