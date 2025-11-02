import sqlite3

def create_emergency_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_reports (
            report_id TEXT PRIMARY KEY,
            passenger_name TEXT,
            contact_number TEXT,
            emergency_type TEXT,
            description TEXT,
            train_number TEXT,
            coach TEXT,
            seat_number TEXT,
            location TEXT,
            date_reported TEXT,
            status TEXT
        )
    """)
    conn.commit()


    cursor.execute("SELECT COUNT(*) FROM emergency_reports")
    if cursor.fetchone()[0] == 0:
        sample_emergencies = [
            ("E001", "Rahul Sharma", "9876543210", "Medical", "Passenger fainted", "12627", "S2", "34", "Between Delhi and Agra", "2025-11-01", "Resolved"),
            ("E002", "Priya Singh", "9123456789", "Security", "Suspicious luggage found", "12841", "A1", "14", "Chennai Station", "2025-11-02", "In Progress"),
            ("E003", "Amit Kumar", "9988776655", "Fire", "Smoke detected in pantry car", "12951", "B1", "21", "Near Kota", "2025-11-03", "Resolved"),
            ("E004", "Neha Patel", "9765432109", "Medical", "Child injured during boarding", "12723", "S4", "10", "Vijayawada", "2025-11-04", "Pending"),
            ("E005", "Ravi Verma", "9456123789", "Technical", "Brake issue reported", "12659", "S3", "17", "Nagpur", "2025-11-05", "Resolved"),
            ("E006", "Sneha Reddy", "9090909090", "Security", "Unauthorized person onboard", "12760", "A2", "06", "Hyderabad", "2025-11-06", "In Progress"),
            ("E007", "Vikram Das", "9543216789", "Fire", "Burning smell from AC unit", "12009", "C1", "02", "Jhansi", "2025-11-07", "Resolved"),
            ("E008", "Kiran Nair", "9845012345", "Medical", "Passenger diabetic shock", "16382", "S6", "59", "Mumbai", "2025-11-08", "Pending"),
            ("E009", "Deepika Rao", "9998887776", "Technical", "Generator failure reported", "12533", "B2", "28", "Lucknow", "2025-11-09", "Resolved"),
            ("E010", "Arjun Mehta", "9001234567", "Security", "Theft of luggage", "12615", "S1", "49", "Chennai", "2025-11-10", "In Progress"),
        ]

        cursor.executemany("""
            INSERT INTO emergency_reports (
                report_id, passenger_name, contact_number,
                emergency_type, description, train_number,
                coach, seat_number, location, date_reported, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_emergencies)
        conn.commit()
        print("✅ Emergency table created with 10 sample records.")
    else:
        print("ℹ️ Emergency table already exists, skipping data insertion.")


def get_emergency_details(conn: sqlite3.Connection, report_id: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emergency_reports WHERE report_id = ?", (report_id,))
    result = cursor.fetchone()
    if result:
        keys = [
            "report_id", "passenger_name", "contact_number", "emergency_type",
            "description", "train_number", "coach", "seat_number",
            "location", "date_reported", "status"
        ]
        return dict(zip(keys, result))
    else:
        return None