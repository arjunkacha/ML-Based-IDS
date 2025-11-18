import streamlit as st
from auth import require_login, list_users, set_admin, delete_user, rerun_streamlit, generate_invite_code, list_invite_codes, deactivate_invite_code

require_login()

if not st.session_state.get('is_admin'):
    st.error("Access denied. Admin privileges required.")
    st.stop()

st.set_page_config(page_title="Admin - Users", layout="wide")
st.title("🛠️ Admin — User Management")

# --- Users Section ---
st.header("👥 Users")
users = list_users()
if not users:
    st.info("No users in the system yet.")
else:
    df = []
    for u in users:
        df.append({'id': u.id, 'username': u.username, 'email': u.email, 'is_admin': u.is_admin, 'created_at': u.created_at})
    st.dataframe(df)

st.write('---')
st.subheader('Manage User')
sel_user = st.text_input('Username')
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Promote to Admin') and sel_user:
        ok, msg = set_admin(sel_user, True)
        if ok:
            st.success('Promoted')
            rerun_streamlit()
        else:
            st.error(msg)
with col2:
    if st.button('Demote from Admin') and sel_user:
        ok, msg = set_admin(sel_user, False)
        if ok:
            st.success('Demoted')
            rerun_streamlit()
        else:
            st.error(msg)
with col3:
    if st.button('Delete User') and sel_user:
        ok, msg = delete_user(sel_user)
        if ok:
            st.success('Deleted')
            rerun_streamlit()
        else:
            st.error(msg)

# --- Invite Codes Section ---
st.write('---')
st.header("🎟️ Invite Codes")
st.subheader('Generate Invite Code')
if st.button('Generate New Invite Code'):
    ok, result = generate_invite_code(st.session_state['user'])
    if ok:
        st.success(f"Generated: `{result}`")
        st.info("Share this code with someone you want to invite. They must use it during signup.")
    else:
        st.error(result)

st.subheader('Active Invite Codes')
invites = list_invite_codes()
if not invites:
    st.info("No invite codes yet.")
else:
    invite_data = []
    for inv in invites:
        invite_data.append({
            'code': inv.code,
            'created_by': inv.created_by,
            'created_at': inv.created_at,
            'used_by': inv.used_by or '(unused)',
            'is_active': inv.is_active
        })
    st.dataframe(invite_data)

st.subheader('Deactivate Invite Code')
code_to_deactivate = st.text_input('Invite Code to Deactivate')
if st.button('Deactivate') and code_to_deactivate:
    ok, msg = deactivate_invite_code(code_to_deactivate)
    if ok:
        st.success('Deactivated')
        rerun_streamlit()
    else:
        st.error(msg)
