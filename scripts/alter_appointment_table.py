from app.database import engine
from sqlalchemy import text

def alter_table():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE appointments ADD COLUMN complaint VARCHAR(500);"))
            print("Successfully added 'complaint' column.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    alter_table()
