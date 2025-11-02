import sqlite3
def create_complaints_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_name TEXT,
            pnr_number TEXT,
            contact_number TEXT,
            category TEXT,             -- e.g. Cleanliness, Delay, Staff behavior
            description TEXT,
            complaint_date TEXT,
            status TEXT,               -- Pending, In Progress, Resolved
            resolution_remarks TEXT
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Rahul Sharma", "1234567890", "9876543210", "Cleanliness", "Coach was not clean", "2025-10-25", "Resolved", "Coach cleaned and inspected."),
            ("Priya Singh", "2345678901", "9876501234", "Delay", "Train delayed by 3 hours", "2025-10-26", "Pending", ""),
            ("Amit Kumar", "3456789012", "9876512345", "Catering", "Poor food quality in pantry car", "2025-10-27", "In Progress", "Vendor notified for action."),
            ("Neha Patel", "4567890123", "9876523456", "Staff behavior", "Rude staff at boarding", "2025-10-28", "Resolved", "Staff counseled and warned."),
            ("Ravi Verma", "5678901234", "9876534567", "Seat Issue", "Double booking on same seat", "2025-10-29", "Pending", ""),
        ]

        cursor.executemany("""
            INSERT INTO complaints (
                passenger_name, pnr_number, contact_number, category,
                description, complaint_date, status, resolution_remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        conn.commit()
        print("✅ Complaints table created with 5 sample records.")
    else:
        print("ℹ️ Complaints table already exists, skipping data insertion.")


# 2️⃣ Register a new complaint

def register_complaint(conn: sqlite3.Connection, passenger_name: str, pnr_number: str, contact_number: str, category: str, description: str):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (
            passenger_name, pnr_number, contact_number, category, description, complaint_date, status
        ) VALUES (?, ?, ?, ?, ?, date('now'), 'Pending')
    """, (passenger_name, pnr_number, contact_number, category, description))
    conn.commit()
    return cursor.lastrowid  


# 3️⃣ Fetch complaint details by PNR or Complaint ID
def get_complaint_details(conn: sqlite3.Connection, pnr_number: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE pnr_number = ?", (pnr_number,))
    result = cursor.fetchall()
    keys = [
        "complaint_id", "passenger_name", "pnr_number", "contact_number",
        "category", "description", "complaint_date", "status", "resolution_remarks"
    ]
    return [dict(zip(keys, row)) for row in result]



# 4️⃣ Update complaint status
def update_complaint_status(conn: sqlite3.Connection, complaint_id: int, status: str, remarks: str = ""):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints
        SET status = ?, resolution_remarks = ?
        WHERE complaint_id = ?
    """, (status, remarks, complaint_id))
    conn.commit()
    return cursor.rowcount > 0  # returns True if updated successfully