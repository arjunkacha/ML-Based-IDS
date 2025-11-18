from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError
from database_setup import Session, User, InviteCode, InviteRequest, create_alert_table
from datetime import datetime
import streamlit as st
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Initialize DB tables if not present
try:
    create_alert_table()
except Exception:
    pass


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(hash: str, password: str) -> bool:
    return pbkdf2_sha256.verify(password, hash)


def create_user(username: str, password: str, email: str = None, is_admin: bool = False):
    session = Session()
    try:
        user = User(username=username, email=email, password_hash=hash_password(password), is_admin=is_admin, created_at=datetime.now())
        session.add(user)
        session.commit()
        return True, "User created"
    except IntegrityError as e:
        session.rollback()
        return False, "Username or email already exists"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def authenticate_user(username: str, password: str):
    session = Session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False, "User not found"
        if verify_password(user.password_hash, password):
            return True, user
        else:
            return False, "Invalid credentials"
    finally:
        session.close()


def get_user(username: str):
    session = Session()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()


def list_users():
    session = Session()
    try:
        return session.query(User).order_by(User.created_at.desc()).all()
    finally:
        session.close()


def set_admin(username: str, is_admin: bool):
    session = Session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False, "User not found"
        user.is_admin = is_admin
        session.commit()
        return True, "Updated"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def delete_user(username: str):
    session = Session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False, "User not found"
        session.delete(user)
        session.commit()
        return True, "Deleted"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def rerun_streamlit():
    """Attempt to rerun the Streamlit script in a backwards-compatible way.

    Tries `st.experimental_rerun()` first, then falls back to changing
    the query params which also triggers a rerun, and finally shows a
    message asking the user to refresh.
    """
    import streamlit as st
    try:
        st.experimental_rerun()
        return
    except Exception:
        try:
            import time
            # Changing query params triggers a rerun in Streamlit
            st.experimental_set_query_params(_rerun=int(time.time()))
            return
        except Exception:
            st.warning("Please refresh the page to complete the action.")


def require_login():
    """Streamlit helper that blocks page if user not logged in."""
    if 'user' in st.session_state and st.session_state['user']:
        return True
    st.warning("Please login via the 'Auth' page before accessing this page.")
    st.stop()


def generate_invite_code(created_by: str):
    """Generate a new invite code. Only admins should call this."""
    session = Session()
    try:
        code = str(uuid.uuid4())[:12]  # Short unique code
        invite = InviteCode(code=code, created_by=created_by, created_at=datetime.now())
        session.add(invite)
        session.commit()
        return True, code
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def validate_invite_code(code: str):
    """Validate if an invite code exists and is active."""
    session = Session()
    try:
        invite = session.query(InviteCode).filter(
            InviteCode.code == code,
            InviteCode.is_active == True,
            InviteCode.used_by == None
        ).first()
        if invite:
            return True, invite
        return False, "Invalid or already used invite code"
    finally:
        session.close()


def mark_invite_used(code: str, used_by: str):
    """Mark an invite code as used."""
    session = Session()
    try:
        invite = session.query(InviteCode).filter(InviteCode.code == code).first()
        if not invite:
            return False, "Code not found"
        invite.used_by = used_by
        invite.used_at = datetime.now()
        session.commit()
        return True, "Marked"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def list_invite_codes():
    """List all invite codes (for admins)."""
    session = Session()
    try:
        return session.query(InviteCode).order_by(InviteCode.created_at.desc()).all()
    finally:
        session.close()


def deactivate_invite_code(code: str):
    """Deactivate an invite code."""
    session = Session()
    try:
        invite = session.query(InviteCode).filter(InviteCode.code == code).first()
        if not invite:
            return False, "Code not found"
        invite.is_active = False
        session.commit()
        return True, "Deactivated"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def send_email(to_email: str, subject: str, body: str):
    """Send email via SMTP. Configure SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD in .env"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')

        if not sender_email or not sender_password:
            return False, "Email configuration not set in environment"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True, "Email sent"
    except Exception as e:
        return False, str(e)


def create_invite_request(full_name: str, email: str, reason: str = ""):
    """Submit an invite request."""
    session = Session()
    try:
        request = InviteRequest(
            full_name=full_name,
            email=email,
            reason=reason,
            status='pending',
            requested_at=datetime.now()
        )
        session.add(request)
        session.commit()
        return True, "Request submitted"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def list_invite_requests(status: str = None):
    """List invite requests, optionally filtered by status."""
    session = Session()
    try:
        query = session.query(InviteRequest).order_by(InviteRequest.requested_at.desc())
        if status:
            query = query.filter(InviteRequest.status == status)
        return query.all()
    finally:
        session.close()


def approve_invite_request(request_id: int, approved_by: str):
    """Approve an invite request, generate code, and send email."""
    session = Session()
    try:
        req = session.query(InviteRequest).filter(InviteRequest.id == request_id).first()
        if not req:
            return False, "Request not found"
        if req.status != 'pending':
            return False, f"Request is already {req.status}"

        # Generate invite code
        code = str(uuid.uuid4())[:12]
        invite = InviteCode(code=code, created_by=approved_by, created_at=datetime.now())
        session.add(invite)

        # Update request
        req.status = 'approved'
        req.approved_by = approved_by
        req.approved_at = datetime.now()
        req.invite_code = code
        session.commit()

        # Send email
        email_body = f"""
        <html>
            <body>
                <h2>Your Invite Code is Ready!</h2>
                <p>Hi {req.full_name},</p>
                <p>Your request for an invite code has been approved.</p>
                <p><strong>Your Invite Code:</strong> <code style="background-color: #f0f0f0; padding: 10px; font-size: 18px;">{code}</code></p>
                <p>Use this code to sign up on our IDS Dashboard.</p>
                <p>This code is valid for one-time use.</p>
                <p>Best regards,<br>IDS Admin Team</p>
            </body>
        </html>
        """
        ok, msg = send_email(req.email, "Your IDS Invite Code", email_body)

        if ok:
            return True, f"Approved and email sent to {req.email}"
        else:
            return True, f"Approved but email failed: {msg}"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def reject_invite_request(request_id: int, rejection_reason: str = ""):
    """Reject an invite request and send rejection email."""
    session = Session()
    try:
        req = session.query(InviteRequest).filter(InviteRequest.id == request_id).first()
        if not req:
            return False, "Request not found"
        if req.status != 'pending':
            return False, f"Request is already {req.status}"

        req.status = 'rejected'
        req.rejection_reason = rejection_reason
        session.commit()

        # Send rejection email
        email_body = f"""
        <html>
            <body>
                <h2>Invite Request Status</h2>
                <p>Hi {req.full_name},</p>
                <p>We regret to inform you that your invite request has been rejected.</p>
                <p><strong>Reason:</strong> {rejection_reason or 'No reason provided'}</p>
                <p>Please contact support for more information.</p>
                <p>Best regards,<br>IDS Admin Team</p>
            </body>
        </html>
        """
        ok, msg = send_email(req.email, "Invite Request Decision", email_body)

        if ok:
            return True, f"Rejected and email sent to {req.email}"
        else:
            return True, f"Rejected but email failed: {msg}"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


