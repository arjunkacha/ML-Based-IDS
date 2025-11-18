import streamlit as st
from auth import create_invite_request

st.set_page_config(page_title="Request Invite", layout="centered")
st.title("📬 Request Invite Code")
st.write("Don't have an invite code? Submit a request below and an admin will review it.")

st.info("Fill in your details and submit a request. An admin will review and send you an invite code via email if approved.")

full_name = st.text_input("Full Name", placeholder="John Doe")
email = st.text_input("Email Address", placeholder="john@example.com")
reason = st.text_area("Why do you need access? (Optional)", placeholder="Brief reason or use case...")

if st.button("Submit Request", type="primary"):
    if not full_name or not email:
        st.error("Full Name and Email are required.")
    elif '@' not in email:
        st.error("Please enter a valid email address.")
    else:
        ok, msg = create_invite_request(full_name, email, reason)
        if ok:
            st.success("✅ Request submitted successfully! Please check your email for updates.")
            st.balloons()
        else:
            st.error(f"Error: {msg}")

st.write("---")
st.info("Already have an invite code? Go to the Auth page and click 'Sign Up'.")
