import streamlit as st
import pandas as pd

from model import load_model, predict
from utils import load_trusted, calculate_risk, log_device

st.title("🔐 AI WiFi Security System")


# Train model button
if st.sidebar.button("Train Model"):
    train_model()


model = load_model()
trusted_macs = load_trusted()


# Inputs
mac = st.text_input("MAC Address")
data_usage = st.number_input("Data Usage (MB)", 0)
time = st.number_input("Time (0-23)", 0, 23)


# Check device
if st.button("Check Device"):

    risk = calculate_risk(data_usage, time)

    st.write(f"⚠ Risk Score: {risk}/100")

   import pandas as pd
import joblib

# Load trained model
model = joblib.load("model.pkl")

# Example device data (you can change values)
data_usage = 1800
time = 2

new_data = pd.DataFrame({
    'DataUsage': [data_usage],
    'Time': [time]
})

result = model.predict(new_data)

if result[0] == -1:
    print("⚠ Unauthorized Device Detected")
else:
    print("✅ Safe Device")