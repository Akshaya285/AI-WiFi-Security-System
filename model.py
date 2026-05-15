import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

data = pd.read_csv("dataset.csv")

X = data[['DataUsage', 'Time']]

model = IsolationForest(contamination=0.3)
model.fit(X)

joblib.dump(model, "model.pkl")

print("Model trained successfully!")