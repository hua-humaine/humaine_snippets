import os
from kfp import dsl

# Example pipeline code that wants to use Humaine Image (humaineImage=true by default)

@dsl.component(base_image="python:3.13-slim")
def train_model_op():
    import pandas as pd
    from sklearn.datasets import make_classification
    # ... code ...
    print("Training component running...")

@dsl.pipeline(name='pipeline-with-compiler-and-humaine-image')
def my_pipeline(): 
    train_task = train_model_op()

if __name__ == "__main__":
    from kfp import compiler
    import sys
     
    compiler.Compiler().compile(
        pipeline_func=my_pipeline,
        package_path='pipeline_temp.yaml'
    )