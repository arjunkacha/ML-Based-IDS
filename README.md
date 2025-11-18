# Machine Learning-Based Hybrid Intrusion Detection System (IDS)

## Project Overview
This project implements a hybrid IDS using supervised (Random Forest) and unsupervised (Autoencoder) machine learning models to detect network threats in the CICIDS2017 dataset and live network traffic.

## Setup Instructions

### 1. Clone the repository and enter the directory
```powershell
git clone <your-repo-url>
cd ML-Based-IDS
```

### 2. Create and activate a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure database (optional: set DATABASE_URL in .env or environment)
```powershell
# For PostgreSQL:
$env:DATABASE_URL = 'postgresql://postgres:password@localhost:5432/ids_db'

# Or for SQLite (recommended for quick local testing):
$env:DATABASE_URL = 'sqlite:///ids_db.sqlite3'
```

### 5. Initialize database tables
```powershell
python -c "import database_setup; database_setup.create_tables()"
```

### 6. Create admin user
```powershell
python - <<'PY'
from auth import create_user
ok,msg = create_user('admin','AdminPassword123','admin@example.com', is_admin=True)
print(ok,msg)
PY
```

### 7. Prepare the dataset
- Place CICIDS2017 CSV files in `MachineLearningCSV/MachineLearningCVE/`.
- Run preprocessing and training scripts:
```powershell
python data_preprocessing.py
python train_models.py
python train_autoencoder.py
```

### 8. Run the Streamlit app
```powershell
streamlit run main_app.py
```

## Authentication & User Management

This system uses **invite-code based signup** for security with two workflows:

### Workflow 1: Direct Admin Invite (Manual)
1. Admin logs in and goes to **Admin — User Management** page.
2. Admin clicks **Generate New Invite Code** and manually shares the code with users.
3. User enters the code during signup on the Auth page.

### Workflow 2: User Request (Recommended)
1. New users visit **Request Invite** page and submit their details (name, email, reason).
2. Request is stored in the database and displayed on **Admin — Invite Requests** dashboard.
3. Admin reviews requests and clicks **Approve** or **Reject**.
4. On approval:
   - A unique invite code is generated and stored.
   - The code is sent to the user's email automatically.
5. User receives the code via email and uses it during signup.
6. After signup, the code is marked as used.

### Email Configuration (For Automated Invite Delivery)
To enable email notifications, configure SMTP settings in `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

**For Gmail:**
- Use an app-specific password (not your regular password).
- Generate one here: https://myaccount.google.com/apppasswords

**For other providers (Outlook, Office365, etc.), update SMTP_SERVER and SMTP_PORT accordingly.**

### Admin Actions
Admins can:
- View and manage all invite requests (pending, approved, rejected).
- Approve requests → code is generated and sent via email.
- Reject requests with optional reason → rejection email is sent.
- View all users and invite code history.
- Manually generate invite codes for direct sharing.

## Notes
- For live packet capture, run PowerShell as Administrator and ensure Npcap is installed.
- Update interface names in `pages/2_Live_Analysis.py` as needed for your system.
- Model files (`.pkl`, `.keras`) must be present in the project root for the app to function.
- All user credentials, invite codes, and requests are stored in the database (PostgreSQL or SQLite).

## Pages Overview
- **Auth** (`pages/0_Auth.py`): Login/signup/logout.
- **Request Invite** (`pages/4_Request_Invite.py`): Submit invite request (no login required).
- **File Analysis** (`pages/1_File_Analysis.py`): Upload CSV and run predictions (requires login).
- **Live Analysis** (`pages/2_Live_Analysis.py`): Real-time network traffic sniffing and analysis (requires login).
- **Model Performance** (`pages/3_Model_Performance.py`): View model metrics, ROC curves, and alert history (requires login).
- **Admin — User Management** (`pages/admin_users.py`): User and invite code management (requires admin login).
- **Admin — Invite Requests** (`pages/5_Admin_Invite_Requests.py`): Review and approve/reject user requests (requires admin login).

## Requirements
See `requirements.txt` for pinned package versions.

