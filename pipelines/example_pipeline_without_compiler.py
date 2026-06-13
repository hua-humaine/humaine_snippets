import os
from kfp import dsl

# Example pipeline code that does NOT have COMPILER and does NOT want to use Humaine Image (humaineImage=false)

@dsl.component(base_image="python:3.13-slim", humaineImage=False)
def train_model_op():
    import pandas as pd
    from sklearn.datasets import make_classification
    # ... code ...
    print("Training component running..")

@dsl.pipeline(name='pipeline-without-compiler-and-humaine-image')
def my_pipeline(): 
    train_task = train_model_op()
