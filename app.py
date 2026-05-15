import streamlit as st
import pandas as pd
import joblib
import random
import time
import matplotlib.pyplot as plt
import socket
import base64

from scapy.all import ARP, Ether, srp
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="WiFi Security System",
    layout="wide"
)

st.title(
    "🔐 AI-Based Unauthorized WiFi Device Detection System"
)

# -------------------------
# AUDIO INITIALIZER
# -------------------------

st.markdown(
    """
    <script>
    document.addEventListener('click', function() {
        const audio = new Audio('alarm.mp3');
        audio.volume = 1.0;
    }, {once:true});
    </script>
    """,
    unsafe_allow_html=True
)

# -------------------------
# SESSION STATE
# -------------------------

if "alert_count" not in st.session_state:
    st.session_state.alert_count = 0

# -------------------------
# DEMO MODE
# -------------------------

demo_mode = st.toggle("🎓 Demo Mode")

if demo_mode:
    st.success("🎓 DEMO MODE ACTIVE")
else:
    st.info("📡 LIVE MODE ACTIVE")

# -------------------------
# LOAD MODEL
# -------------------------

model = joblib.load("model.pkl")

# -------------------------
# LOAD TRUSTED DEVICES
# -------------------------

trusted = pd.read_csv(
    "trusted_devices.csv"
)

trusted_macs = trusted["MAC"].tolist()

# -------------------------
# LOAD LOGS
# -------------------------

def load_logs():

    try:

        return pd.read_csv(
            "logs.csv"
        )

    except:

        return pd.DataFrame(
            columns=[
                "MAC",
                "DataUsage",
                "Time",
                "Risk",
                "Result"
            ]
        )

# -------------------------
# SAVE LOGS
# -------------------------

def save_logs(log):

    try:

        old_logs = pd.read_csv(
            "logs.csv"
        )

    except:

        old_logs = pd.DataFrame(
            columns=[
                "MAC",
                "DataUsage",
                "Time",
                "Risk",
                "Result"
            ]
        )

    updated_logs = pd.concat(
        [old_logs, log],
        ignore_index=True
    )

    updated_logs.to_csv(
        "logs.csv",
        index=False
    )

# -------------------------
# SIREN ALARM FUNCTION
# -------------------------

def play_alarm():

    try:

        with open(
            "alarm.mp3",
            "rb"
        ) as audio_file:

            audio_bytes = audio_file.read()

        encoded_audio = base64.b64encode(
            audio_bytes
        ).decode()

        audio_html = f"""
        <audio autoplay>
            <source
            src="data:audio/mp3;base64,{encoded_audio}"
            type="audio/mp3">
        </audio>
        """

        st.markdown(
            audio_html,
            unsafe_allow_html=True
        )

        st.error(
            "🚨 SECURITY ALERT 🚨"
        )

        st.toast(
            "🚨 SIREN ACTIVATED!"
        )

    except:

        st.error(
            "⚠ alarm.mp3 missing"
        )

# -------------------------
# NETWORK SCAN
# -------------------------

def scan_network():

    try:

        hostname = socket.gethostname()

        local_ip = socket.gethostbyname(
            hostname
        )

        ip_parts = local_ip.split(".")

        target_ip = (
            f"{ip_parts[0]}."
            f"{ip_parts[1]}."
            f"{ip_parts[2]}.0/24"
        )

        arp = ARP(
            pdst=target_ip
        )

        ether = Ether(
            dst="ff:ff:ff:ff:ff:ff"
        )

        result = srp(
            ether / arp,
            timeout=3,
            verbose=0
        )[0]

        devices = []

        for _, rcv in result:

            devices.append({
                "IP": rcv.psrc,
                "MAC": rcv.hwsrc
            })

        return devices

    except:

        return []

# -------------------------
# DASHBOARD
# -------------------------

st.subheader("📊 Dashboard")

logs = load_logs()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Logs",
    len(logs)
)

col2.metric(
    "Unauthorized",
    len(
        logs[
            logs["Result"]
            == "Unauthorized"
        ]
    )
)

col3.metric(
    "Alerts",
    st.session_state.alert_count
)

# -------------------------
# MANUAL ANALYSIS
# -------------------------

st.subheader("🧠 Manual Analysis")

mac = st.text_input(
    "MAC Address"
)

data_usage = st.number_input(
    "Data Usage (MB)",
    min_value=0
)

time_val = st.number_input(
    "Time (0-23)",
    min_value=0,
    max_value=23
)

if st.button("Analyze Device"):

    input_data = pd.DataFrame([{
        "DataUsage": data_usage,
        "Time": time_val
    }])

    prediction = model.predict(
        input_data
    )

    risk = (
        data_usage / 2000
    ) * 70

    if time_val <= 5:
        risk += 30

    risk = int(
        min(risk, 100)
    )

    if (
        prediction[0] == -1
        or mac not in trusted_macs
    ):

        result = "Unauthorized"

    elif risk > 70:

        result = "Suspicious"

    else:

        result = "Safe"

    st.write(f"MAC: {mac}")

    st.write(
        f"Risk Score: {risk}/100"
    )

    if result == "Safe":

        st.success(
            "✅ Safe Device"
        )

    elif result == "Suspicious":

        st.warning(
            "⚠ Suspicious Device"
        )

    else:

        st.error(
            "🚨 Unauthorized Device"
        )

        st.session_state.alert_count += 1

        play_alarm()

    log = pd.DataFrame([{
        "MAC": mac,
        "DataUsage": data_usage,
        "Time": time_val,
        "Risk": risk,
        "Result": result
    }])

    save_logs(log)

    st.rerun()

# -------------------------
# SIMULATION MODE
# -------------------------

st.subheader("🎮 Simulation Mode")

if st.button(
    "Start Simulation"
):

    for i in range(5):

        mac_auto = random.choice([
            "A1:B2:C3",
            "D4:E5:F6",
            "HACKER_X"
        ])

        usage = random.randint(
            100,
            2500
        )

        time_auto = random.randint(
            0,
            23
        )

        input_data = pd.DataFrame([{
            "DataUsage": usage,
            "Time": time_auto
        }])

        prediction = model.predict(
            input_data
        )

        risk = (
            usage / 2000
        ) * 70

        if time_auto <= 5:
            risk += 30

        risk = int(
            min(risk, 100)
        )

        if (
            prediction[0] == -1
            or mac_auto not in trusted_macs
        ):

            result = "Unauthorized"

        elif risk > 70:

            result = "Suspicious"

        else:

            result = "Safe"

        st.write(
            f"Checking: {mac_auto}"
        )

        st.write(
            f"Risk Score: {risk}"
        )

        if result == "Safe":

            st.success(
                "✅ Safe Device"
            )

        elif result == "Suspicious":

            st.warning(
                "⚠ Suspicious Device"
            )

        else:

            st.error(
                "🚨 Unauthorized Device"
            )

            st.session_state.alert_count += 1

            play_alarm()

        log = pd.DataFrame([{
            "MAC": mac_auto,
            "DataUsage": usage,
            "Time": time_auto,
            "Risk": risk,
            "Result": result
        }])

        save_logs(log)

        time.sleep(1)

    st.rerun()

# -------------------------
# NETWORK SCANNER
# -------------------------

st.subheader(
    "📡 Network Scanner"
)

if st.button(
    "Scan Network"
):

    if demo_mode:

        devices = [
            {
                "IP": "192.168.1.2",
                "MAC": "AA:BB:CC:01"
            },
            {
                "IP": "192.168.1.3",
                "MAC": "UNAUTH_DEVICE"
            }
        ]

    else:

        devices = scan_network()

    if devices:

        device_df = pd.DataFrame(
            devices
        )

        st.dataframe(device_df)

        for device in devices:

            mac_scan = device["MAC"]

            if (
                mac_scan
                not in trusted_macs
            ):

                result = "Unauthorized"

                st.session_state.alert_count += 1

                st.error(
                    f"🚨 Unauthorized Device: {mac_scan}"
                )

                play_alarm()

            else:

                result = "Safe"

                st.success(
                    f"✅ Trusted Device: {mac_scan}"
                )

            log = pd.DataFrame([{
                "MAC": mac_scan,
                "DataUsage": 0,
                "Time": 0,
                "Risk": 0,
                "Result": result
            }])

            save_logs(log)

    else:

        st.warning(
            "⚠ No devices detected"
        )

    st.rerun()

# -------------------------
# LOGS
# -------------------------

st.subheader("📁 Logs")

if st.button("Clear Logs"):

    pd.DataFrame(
        columns=[
            "MAC",
            "DataUsage",
            "Time",
            "Risk",
            "Result"
        ]
    ).to_csv(
        "logs.csv",
        index=False
    )

    st.session_state.alert_count = 0

    st.success(
        "✅ Logs Cleared"
    )

    st.rerun()

st.dataframe(
    load_logs()
)

# -------------------------
# PIE CHART
# -------------------------

st.subheader(
    "📈 Analysis"
)

logs = load_logs()

if not logs.empty:

    fig, ax = plt.subplots(
        figsize=(3.5, 3.5)
    )

    logs[
        "Result"
    ].value_counts().plot.pie(
        autopct="%1.1f%%",
        ax=ax,
        startangle=90
    )

    ax.set_ylabel("")

    st.pyplot(fig)

# -------------------------
# PDF REPORT
# -------------------------

st.subheader(
    "📄 PDF Report"
)

if not logs.empty:

    if st.button(
        "Generate PDF"
    ):

        doc = SimpleDocTemplate(
            "wifi_report.pdf"
        )

        styles = getSampleStyleSheet()

        elements = []

        elements.append(
            Paragraph(
                "WiFi Security Report",
                styles["Title"]
            )
        )

        elements.append(
            Spacer(1, 12)
        )

        for _, row in logs.iterrows():

            text = f"""
            MAC: {row['MAC']}<br/>
            Risk: {row['Risk']}<br/>
            Result: {row['Result']}<br/><br/>
            """

            elements.append(
                Paragraph(
                    text,
                    styles["BodyText"]
                )
            )

        doc.build(
            elements
        )

        st.success(
            "✅ PDF Generated"
        )

        with open(
            "wifi_report.pdf",
            "rb"
        ) as f:

            st.download_button(
                "Download Report",
                f,
                "wifi_report.pdf"
            )