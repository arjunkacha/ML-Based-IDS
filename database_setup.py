from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# --- Database Configuration ---
# Read DATABASE_URL from environment, fallback to local default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:darsh@localhost:5432/ids_db')

# --- SQLAlchemy Setup ---
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# --- Define Alert Model ---
class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(Integer)
    total_length_fwd_packets = Column(Integer)
    known_attack_type = Column(String)
    anomaly_detected = Column(Boolean)

    # You might want to add more columns from your packet features later
    # For now, let's keep it concise.
    # Eg: source_ip = Column(String)
    # Eg: dest_ip = Column(String)

    def __repr__(self):
        return (f"<Alert(id={self.id}, timestamp='{self.timestamp}', "
                f"known_attack='{self.known_attack_type}', anomaly='{self.anomaly_detected}')>")


# --- Define User Model for Authentication ---
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# --- Define InviteCode Model for Signup Control ---
class InviteCode(Base):
    __tablename__ = 'invite_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    created_by = Column(String, nullable=False)  # username of admin who created it
    created_at = Column(DateTime, default=datetime.now)
    used_by = Column(String, nullable=True)  # username who used it
    used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<InviteCode(code='{self.code}', created_by='{self.created_by}', used_by='{self.used_by}')>"


# --- Define InviteRequest Model for User Requests ---
class InviteRequest(Base):
    __tablename__ = 'invite_requests'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, default='pending')  # pending, approved, rejected
    requested_at = Column(DateTime, default=datetime.now)
    approved_by = Column(String, nullable=True)  # admin username who approved
    approved_at = Column(DateTime, nullable=True)
    invite_code = Column(String, nullable=True)  # assigned code after approval
    rejection_reason = Column(Text, nullable=True)

    def __repr__(self):
        return f"<InviteRequest(id={self.id}, email='{self.email}', status='{self.status}')>"

# --- Create Table ---
def create_alert_table():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully or already exist.")
    except Exception as e:
        print(f"Error creating table: {e}")


def create_tables():
    """Alias for create_alert_table kept for backward compatibility."""
    create_alert_table()

if __name__ == "__main__":
    create_alert_table()