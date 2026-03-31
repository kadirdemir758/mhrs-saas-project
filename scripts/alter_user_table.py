from app.database import engine
from sqlalchemy import text

def alter_user_table():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN verification_code VARCHAR(6);"))
            print("Successfully added 'verification_code' column to users table.")
        except Exception as e:
            print(f"Error (maybe already exists?): {e}")

if __name__ == "__main__":
    alter_user_table()
