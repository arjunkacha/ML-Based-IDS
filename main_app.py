import streamlit as st

st.set_page_config(
    page_title="Hybrid IDS Project",
    layout="wide"
)

st.title("🛡️ Machine Learning-Based Hybrid Intrusion Detection System")
st.sidebar.success("Select an analysis method above.")

st.header("Welcome to the IDS Dashboard!")
st.write(
    "This project implements a hybrid Intrusion Detection System (IDS) that uses "
    "both supervised and unsupervised machine learning models to detect network threats."
)
st.write("---")

st.subheader("Features:")
st.markdown("""
- **File-Based Analysis:** Upload a CSV file containing network traffic data (from the CICIDS2017 dataset) to get a full prediction report.
- **Live Network Analysis:** Start a real-time sniffer to analyze live traffic on your network and get immediate alerts for known attacks and unknown anomalies.
""")

st.subheader("How to Use:")
st.markdown("""
1.  Select an analysis method from the sidebar on the left.
2.  Follow the instructions on the selected page to either upload a file or start the live capture.
""")