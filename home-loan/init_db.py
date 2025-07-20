import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "home_loan.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Loans table
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY,
            loan_account_number TEXT UNIQUE,
            sanctioned_amount REAL,
            interest_start_date DATE,
            emi_start_date DATE,
            interest_rate REAL,
            tenure_months INTEGER,
            emi_amount REAL,
            is_fully_disbursed BOOLEAN,
            notes TEXT
        )
    ''')
    # Disbursements table
    c.execute('''
        CREATE TABLE IF NOT EXISTS disbursements (
            id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            date DATE,
            amount REAL,
            note TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans(id)
        )
    ''')
    # Prepayments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS prepayments (
            id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            date DATE,
            amount REAL,
            note TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans(id)
        )
    ''')
    # EMI Payments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS emi_payments (
            id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            installment_num INTEGER,
            scheduled_due_date DATE,
            actual_payment_date DATE,
            amount_paid REAL,
            status TEXT,
            note TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans(id)
        )
    ''')
    # Amortization Schedule table
    c.execute('''
        CREATE TABLE IF NOT EXISTS amortization_schedule (
            id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            installment_num INTEGER,
            emi_due_date DATE,
            opening_principal REAL,
            emi_amount REAL,
            principal_component REAL,
            interest_component REAL,
            closing_principal REAL,
            applicable_interest_rate REAL,
            total_amount_due REAL,
            FOREIGN KEY (loan_id) REFERENCES loans(id)
        )
    ''')
    # Simulations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY,
            loan_id INTEGER,
            name TEXT,
            created_at DATE,
            notes TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans(id)
        )
    ''')
    # Simulation Events table
    c.execute('''
        CREATE TABLE IF NOT EXISTS simulation_events (
            id INTEGER PRIMARY KEY,
            simulation_id INTEGER,
            event_type TEXT,
            event_date DATE,
            amount REAL,
            note TEXT,
            FOREIGN KEY (simulation_id) REFERENCES simulations(id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized at", DB_PATH)
