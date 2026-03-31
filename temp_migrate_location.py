import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN city VARCHAR(100);"))
        conn.execute(text("ALTER TABLE users ADD COLUMN district VARCHAR(100);"))
        conn.commit()
        print("Columns added successfully.")
    except Exception as e:
        print(f"Error: {e}")
