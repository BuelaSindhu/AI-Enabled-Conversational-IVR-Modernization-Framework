import sqlite3
import os

# Import all your feature-specific database modules
from app.db import (
    pnr_db,
    complaints_db,
    emergency_db,
    train_schedule_db,
    seat_db,
    refunds_db,
)

# 1️⃣ Define the database file path (inside the same folder)

DB_PATH = os.path.join(os.path.dirname(__file__), "railway_ivr.db")

# 2️⃣ Create a reusable database connection

def get_connection():
    """Return a new SQLite connection to the shared DB file."""
    return sqlite3.connect(DB_PATH)
# 3️⃣ Initialize all tables by calling each module’s setup function

def initialize_all_tables():
    """Create all tables (PNR, complaints, emergency, etc.)"""
    conn = get_connection()

    # Call the create_table() functions from each module
    pnr_db.create_pnr_table(conn)
    complaints_db.create_complaints_table(conn)
    emergency_db.create_emergency_table(conn)
    train_schedule_db.create_train_schedule_table(conn)
    seat_db.create_seat_table(conn)
    refunds_db.create_refunds_table(conn)

    conn.close()
    print("✅ All tables initialized successfully in railway_ivr.db")


if __name__ == "__main__":
    initialize_all_tables()