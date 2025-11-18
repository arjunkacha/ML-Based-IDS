import streamlit as st
from auth import create_user, authenticate_user, get_user, rerun_streamlit, validate_invite_code, mark_invite_used

st.set_page_config(page_title="Auth", layout="centered")
st.title("🔐 Authentication")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        ok, result = authenticate_user(username, password)
        if ok:
            user = result
            st.session_state['user'] = user.username
            st.session_state['user_id'] = user.id
            st.session_state['is_admin'] = user.is_admin
            st.success(f"Logged in as {user.username}")
            rerun_streamlit()
        else:
            st.error(result)

with tab2:
    st.subheader("Sign Up (Invite Required)")
    st.info("Sign up requires an invite code. Contact an administrator to request one.")
    new_username = st.text_input("Choose a username", key="signup_user")
    new_email = st.text_input("Email (optional)", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_pass")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_pass2")
    invite_code = st.text_input("Invite Code", type="password", key="invite_code")
    
    if st.button("Create Account"):
        if not new_username or not new_password or not invite_code:
            st.error("Username, password, and invite code are required.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Validate invite code
            valid, result = validate_invite_code(invite_code)
            if not valid:
                st.error(result)
            else:
                # Create user
                ok, msg = create_user(new_username, new_password, new_email)
                if ok:
                    # Mark invite as used
                    mark_invite_used(invite_code, new_username)
                    st.success("Account created. Please login.")
                else:
                    st.error(msg)

if 'user' in st.session_state and st.session_state['user']:
    st.write(f"Logged in as: {st.session_state['user']}")
    if st.button("Logout"):
        st.session_state['user'] = None
        st.session_state['user_id'] = None
        st.session_state['is_admin'] = None
        st.success("Logged out")
        rerun_streamlit()
