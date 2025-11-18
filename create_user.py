from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import User, DATABASE_URL
from hashing import Hash

# --- Database Connection ---
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_admin_user():
    session = Session()
    try:
        # Check if the user already exists
        existing_user = session.query(User).filter(User.username == 'admin').first()
        if existing_user:
            print("User 'admin' already exists.")
            return

        # Create a new user
        new_user = User(
            username='admin',
            hashed_password=Hash.bcrypt('123') # Set a default password
        )
        session.add(new_user)
        session.commit()
        print("Successfully created admin user with username 'admin' and password 'admin123'.")
        print("Please change this password in a real application!")
    except Exception as e:
        session.rollback()
        print(f"Error creating user: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()