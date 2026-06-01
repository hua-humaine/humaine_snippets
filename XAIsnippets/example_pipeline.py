import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def run_simple_pipeline():
    print("--- Pipeline Started ---")
    
    # 1. Δημιουργία dummy data
    X, y = make_classification(n_samples=100, n_features=4)
    df = pd.DataFrame(X, columns=['f1', 'f2', 'f3', 'f4'])
    print(f"Data Loaded: {df.shape}")
    
    # 2. Εκπαίδευση μοντέλου
    clf = RandomForestClassifier()
    clf.fit(X, y)
    print("Model Trained successfully!")
    
    # 3. Save model
    os.makedirs('models', exist_ok=True)
    joblib.dump(clf, 'models/test_model.pkl')
    print("Model saved to /models/test_model.pkl")
    
    print("--- Pipeline Finished Successfully ---")

if __name__ == "__main__":
    run_simple_pipeline()