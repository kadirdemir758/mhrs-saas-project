from app.database import engine
from sqlalchemy import text
import sys

def run():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL;"))
            print("Migration successful: ADDED phone to users table.")
    except Exception as e:
        print("Migration warning (might already exist):", e)

if __name__ == "__main__":
    run()
