import sqlite3
def create_refunds_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refunds (
            refund_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr_number TEXT,
            passenger_name TEXT,
            train_number TEXT,
            amount REAL,
            payment_mode TEXT,
            refund_status TEXT,
            refund_date TEXT,
            remarks TEXT
        )
    """)
    conn.commit()

    # Insert sample data if empty
    cursor.execute("SELECT COUNT(*) FROM refunds")
    if cursor.fetchone()[0] == 0:
        sample_refunds = [
            ("1234567890", "Rahul Sharma", "12627", 850.00, "UPI", "Processed", "2025-10-25", "Refund credited to bank."),
            ("2345678901", "Priya Singh", "12841", 1250.00, "Credit Card", "Pending", "2025-10-26", "Processing delay due to bank issue."),
            ("3456789012", "Amit Kumar", "12951", 980.50, "Net Banking", "Processed", "2025-10-27", "Refund successful."),
            ("4567890123", "Neha Patel", "12723", 650.00, "UPI", "Failed", "2025-10-28", "UPI ID not valid."),
            ("5678901234", "Ravi Verma", "12659", 1340.00, "Debit Card", "Processed", "2025-10-29", "Refund successful."),
            ("6789012345", "Sneha Reddy", "12760", 720.00, "Wallet", "Processed", "2025-10-30", "Amount added to wallet."),
            ("7890123456", "Vikram Das", "12009", 1600.00, "UPI", "Pending", "2025-10-31", "Awaiting confirmation."),
            ("8901234567", "Kiran Nair", "16382", 940.00, "Credit Card", "Processed", "2025-11-01", "Refund completed."),
            ("9012345678", "Deepika Rao", "12533", 1250.00, "Net Banking", "Processed", "2025-11-02", "Amount credited successfully."),
            ("1122334455", "Arjun Mehta", "12615", 500.00, "UPI", "Failed", "2025-11-03", "Invalid UPI ID."),
        ]

        cursor.executemany("""
            INSERT INTO refunds (
                pnr_number, passenger_name, train_number, amount,
                payment_mode, refund_status, refund_date, remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_refunds)
        conn.commit()
        print(" Refunds table created with 10 sample records.")
    else:
        print("ℹ Refunds table already exists, skipping data insertion.")
def get_refund_status(conn: sqlite3.Connection, pnr_number: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refunds WHERE pnr_number = ?", (pnr_number,))
    result = cursor.fetchone()
    if result:
        keys = [
            "refund_id", "pnr_number", "passenger_name", "train_number",
            "amount", "payment_mode", "refund_status", "refund_date", "remarks"
        ]
        return dict(zip(keys, result))
    else:
        return None