import streamlit as st
from auth import require_login, list_invite_requests, approve_invite_request, reject_invite_request, rerun_streamlit

require_login()

if not st.session_state.get('is_admin'):
    st.error("Access denied. Admin privileges required.")
    st.stop()

st.set_page_config(page_title="Admin - Invite Requests", layout="wide")
st.title("🔔 Admin — Invite Requests")

# --- Filter by Status ---
status_filter = st.selectbox("Filter by Status", ["All", "pending", "approved", "rejected"])
filtered_status = None if status_filter == "All" else status_filter

# --- Get requests ---
requests = list_invite_requests(status=filtered_status)

if not requests:
    st.info(f"No {'pending' if filtered_status == 'pending' else ''} invite requests.".strip())
else:
    st.subheader(f"Total Requests: {len(requests)}")
    
    for req in requests:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_color = "🟡" if req.status == "pending" else ("🟢" if req.status == "approved" else "🔴")
                st.markdown(f"**{status_color} {req.full_name}** | {req.email}")
                st.caption(f"Requested: {req.requested_at.strftime('%Y-%m-%d %H:%M')}")
                if req.reason:
                    st.write(f"*Reason: {req.reason}*")
                
                if req.status == "approved":
                    st.success(f"✅ Approved by {req.approved_by} on {req.approved_at.strftime('%Y-%m-%d %H:%M')}")
                    st.code(req.invite_code, language="text")
                elif req.status == "rejected":
                    st.error(f"❌ Rejected | Reason: {req.rejection_reason or 'N/A'}")
            
            with col2:
                if req.status == "pending":
                    col2a, col2b = st.columns(2)
                    with col2a:
                        if st.button("✅ Approve", key=f"approve_{req.id}"):
                            ok, msg = approve_invite_request(req.id, st.session_state['user'])
                            if ok:
                                st.success(msg)
                                rerun_streamlit()
                            else:
                                st.error(msg)
                    with col2b:
                        if st.button("❌ Reject", key=f"reject_{req.id}"):
                            st.session_state[f'reject_dialog_{req.id}'] = True
                    
                    # Rejection reason dialog
                    if st.session_state.get(f'reject_dialog_{req.id}'):
                        rejection_reason = st.text_input(
                            f"Reason for rejecting {req.full_name}",
                            key=f"reject_reason_{req.id}",
                            placeholder="Optional reason..."
                        )
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("Confirm Rejection", key=f"confirm_reject_{req.id}"):
                                ok, msg = reject_invite_request(req.id, rejection_reason)
                                if ok:
                                    st.success(msg)
                                    rerun_streamlit()
                                else:
                                    st.error(msg)
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_reject_{req.id}"):
                                st.session_state[f'reject_dialog_{req.id}'] = False
                                rerun_streamlit()
            
            st.divider()
