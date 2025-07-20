from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional
import math
import csv
import sqlite3
from pathlib import Path
from datetime import datetime

# Data class representing a single row in the amortization schedule
@dataclass
class AmortizationRow:
    installment_num: int  # The installment number (1-based)
    emi_due_date: date  # The due date for this EMI
    opening_principal: float  # Principal at the start of the period
    emi_amount: float  # Total EMI amount for this installment
    principal_component: float  # Portion of EMI that goes towards principal
    interest_component: float  # Portion of EMI that goes towards interest
    closing_principal: float  # Principal remaining after this installment
    applicable_interest_rate: float  # Interest rate applied for this period
    total_amount_due: float  # Total of all future EMIs after this row

# Data class representing a loan
@dataclass
class Loan:
    loan_account_number: str  # Unique identifier for the loan
    sanctioned_amount: float  # Total loan amount sanctioned
    disbursed_amount: float  # Amount disbursed so far
    interest_start_date: date  # Date when interest calculation starts
    emi_start_date: date  # Date when EMI payments start
    interest_rate: float  # Annual interest rate (percentage)
    tenure_months: int  # Total tenure in months
    emi_amount: float  # EMI amount (to be calculated)
    is_fully_disbursed: bool  # Whether the loan is fully disbursed
    # Add more fields as needed

# Data class representing a prepayment
@dataclass
class Prepayment:
    date: date  # Date of prepayment
    amount: float  # Amount of prepayment
    note: Optional[str] = None  # Optional note

@dataclass
class Disbursement:
    date: date  # Date of disbursement
    amount: float  # Amount disbursed
    note: Optional[str] = None  # Optional note

@dataclass
class RateChange:
    date: date  # Date from which new rate applies
    new_rate: float  # New interest rate
    note: Optional[str] = None

DB_PATH = Path(__file__).parent / "home_loan.db"

# Function to calculate the EMI for a given principal, interest rate, and tenure
# Formula: EMI = [P x R x (1+R)^N] / [(1+R)^N-1]
# Where:
#   P = principal, R = monthly interest rate, N = number of months
# Returns the EMI rounded to 2 decimal places

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate the Equated Monthly Installment (EMI) for a loan.

    Args:
        principal (float): The principal loan amount.
        annual_rate (float): The annual interest rate (in percent).
        tenure_months (int): The loan tenure in months.

    Returns:
        float: The EMI amount, rounded to 2 decimal places.
    """
    r = annual_rate / (12 * 100)  # Convert annual rate to monthly decimal
    emi = principal * r * math.pow(1 + r, tenure_months) / (math.pow(1 + r, tenure_months) - 1)
    return round(emi, 2)

# Function to generate the amortization schedule for a loan
# Returns a list of AmortizationRow objects, one for each installment
# Each row contains the breakdown of principal and interest for that EMI

def generate_amortization_schedule(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    start_date: date
) -> List[AmortizationRow]:
    """
    Generate the amortization schedule for a loan.

    Args:
        principal (float): The principal loan amount.
        annual_rate (float): The annual interest rate (in percent).
        tenure_months (int): The loan tenure in months.
        start_date (date): The date of the first EMI payment.

    Returns:
        List[AmortizationRow]: List of amortization schedule rows, one per installment.
    """
    schedule = []  # List to hold the amortization rows
    emi = calculate_emi(principal, annual_rate, tenure_months)  # Calculate EMI
    outstanding = principal  # Track the outstanding principal
    total_amount_due = emi * tenure_months  # Total of all future EMIs
    for i in range(1, tenure_months + 1):
        # Calculate interest for the current month
        interest = round(outstanding * (annual_rate / (12 * 100)), 2)
        # Principal component is the remainder of EMI after interest
        principal_component = round(emi - interest, 2)
        # Closing principal after this EMI
        closing_principal = round(outstanding - principal_component, 2)
        # Calculate the due date for this EMI (approximate by adding 30 days per month)
        due_date = start_date + timedelta(days=30 * (i - 1))
        # Create the amortization row and add to the schedule
        schedule.append(AmortizationRow(
            installment_num=i,
            emi_due_date=due_date,
            opening_principal=outstanding,
            emi_amount=emi,
            principal_component=principal_component,
            interest_component=interest,
            closing_principal=closing_principal,
            applicable_interest_rate=annual_rate,
            total_amount_due=emi * (tenure_months - i + 1)
        ))
        # Update outstanding principal for next iteration
        outstanding = closing_principal
    return schedule

# Function to generate the amortization schedule for a loan, considering part pre-payments
# Each prepayment is applied at the start of the month (before EMI is calculated for that month)
# If the loan is not fully disbursed, prepayments reduce the EMI
# If fully disbursed, they reduce the tenure

def generate_amortization_schedule_with_prepayments(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    start_date: date,
    prepayments: List[Prepayment],
    is_fully_disbursed: bool
) -> List[AmortizationRow]:
    """
    Generate the amortization schedule for a loan, considering part pre-payments.
    Each prepayment is applied at the start of the month (before EMI is calculated for that month).
    If the loan is not fully disbursed, prepayments reduce the EMI. If fully disbursed, they reduce the tenure.

    Args:
        principal (float): The principal loan amount.
        annual_rate (float): The annual interest rate (in percent).
        tenure_months (int): The loan tenure in months.
        start_date (date): The date of the first EMI payment.
        prepayments (List[Prepayment]): List of prepayment events.
        is_fully_disbursed (bool): Whether the loan is fully disbursed.

    Returns:
        List[AmortizationRow]: List of amortization schedule rows, one per installment.
    """
    schedule = []
    outstanding = principal
    emi = calculate_emi(outstanding, annual_rate, tenure_months)
    prepayments = sorted(prepayments, key=lambda p: p.date)  # Sort by date
    prepay_idx = 0
    i = 1
    current_date = start_date
    remaining_months = tenure_months
    while outstanding > 0.01 and remaining_months > 0:
        # Apply any prepayment for this month (before EMI)
        while prepay_idx < len(prepayments) and prepayments[prepay_idx].date <= current_date:
            prepay = prepayments[prepay_idx]
            outstanding = max(0, outstanding - prepay.amount)
            if not is_fully_disbursed:
                # Recalculate EMI for remaining months if not fully disbursed
                emi = calculate_emi(outstanding, annual_rate, remaining_months)
            # If fully disbursed, tenure will reduce naturally as principal drops
            prepay_idx += 1
        # Calculate interest for the current month
        interest = round(outstanding * (annual_rate / (12 * 100)), 2)
        # Principal component is the remainder of EMI after interest
        principal_component = min(round(emi - interest, 2), outstanding)
        # Closing principal after this EMI
        closing_principal = round(outstanding - principal_component, 2)
        # Create the amortization row and add to the schedule
        schedule.append(AmortizationRow(
            installment_num=i,
            emi_due_date=current_date,
            opening_principal=outstanding,
            emi_amount=emi,
            principal_component=principal_component,
            interest_component=interest,
            closing_principal=closing_principal,
            applicable_interest_rate=annual_rate,
            total_amount_due=emi * (remaining_months)
        ))
        outstanding = closing_principal
        current_date = current_date + timedelta(days=30)
        i += 1
        remaining_months -= 1
        # If fully disbursed and principal is paid off early, break
        if is_fully_disbursed and outstanding <= 0.01:
            break
    return schedule

def print_summary_statistics(schedule: List[AmortizationRow]):
    """
    Print summary statistics for a given amortization schedule.
    Shows total interest paid, total payments, and actual tenure.
    """
    total_interest = sum(row.interest_component for row in schedule)
    total_principal = sum(row.principal_component for row in schedule)
    total_payments = sum(row.emi_amount for row in schedule)
    actual_tenure = len(schedule)
    print("\nSummary Statistics:")
    print(f"  Total Interest Paid:   ₹{total_interest:,.2f}")
    print(f"  Total Principal Paid:  ₹{total_principal:,.2f}")
    print(f"  Total Payments:        ₹{total_payments:,.2f}")
    print(f"  Actual Tenure:         {actual_tenure} months ({actual_tenure//12} years, {actual_tenure%12} months)")

def export_schedule_to_csv(schedule: List[AmortizationRow], filename: str):
    """
    Export the amortization schedule to a CSV file.
    Args:
        schedule (List[AmortizationRow]): The amortization schedule.
        filename (str): The output CSV filename.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Installment Num", "EMI Due Date", "Opening Principal", "EMI Amount",
            "Principal Component", "Interest Component", "Closing Principal",
            "Applicable Rate of Interest (%)", "Total Amount Due (future EMIs)"
        ])
        for row in schedule:
            writer.writerow([
                row.installment_num,
                row.emi_due_date,
                f"{row.opening_principal:.2f}",
                f"{row.emi_amount:.2f}",
                f"{row.principal_component:.2f}",
                f"{row.interest_component:.2f}",
                f"{row.closing_principal:.2f}",
                f"{row.applicable_interest_rate:.2f}",
                f"{row.total_amount_due:.2f}"
            ])
    print(f"\nSchedule exported to {filename}")

def save_loan_to_db(loan, prepayments, schedule):
    """
    Save loan, prepayments, and amortization schedule to the database.
    Args:
        loan (Loan): Loan dataclass instance
        prepayments (List[Prepayment]): List of prepayments
        schedule (List[AmortizationRow]): Amortization schedule
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Insert loan
    c.execute('''
        INSERT OR REPLACE INTO loans (loan_account_number, sanctioned_amount, interest_start_date, emi_start_date, interest_rate, tenure_months, emi_amount, is_fully_disbursed, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        loan.loan_account_number,
        loan.sanctioned_amount,
        loan.interest_start_date.isoformat(),
        loan.emi_start_date.isoformat(),
        loan.interest_rate,
        loan.tenure_months,
        loan.emi_amount,
        int(loan.is_fully_disbursed),
        None
    ))
    loan_id = c.execute('SELECT id FROM loans WHERE loan_account_number = ?', (loan.loan_account_number,)).fetchone()[0]
    # Insert prepayments
    c.execute('DELETE FROM prepayments WHERE loan_id = ?', (loan_id,))
    for p in prepayments:
        c.execute('''
            INSERT INTO prepayments (loan_id, date, amount, note) VALUES (?, ?, ?, ?)
        ''', (loan_id, p.date.isoformat(), p.amount, p.note))
    # Insert amortization schedule
    c.execute('DELETE FROM amortization_schedule WHERE loan_id = ?', (loan_id,))
    for row in schedule:
        c.execute('''
            INSERT INTO amortization_schedule (
                loan_id, installment_num, emi_due_date, opening_principal, emi_amount, principal_component, interest_component, closing_principal, applicable_interest_rate, total_amount_due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            loan_id, row.installment_num, row.emi_due_date.isoformat(), row.opening_principal, row.emi_amount, row.principal_component, row.interest_component, row.closing_principal, row.applicable_interest_rate, row.total_amount_due
        ))
    conn.commit()
    conn.close()
    print(f"Loan and related data saved to DB (loan_account_number={loan.loan_account_number})")

def load_loan_from_db(loan_account_number):
    """
    Load loan, prepayments, and amortization schedule from the database.
    Returns: (Loan, List[Prepayment], List[AmortizationRow])
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Load loan
    c.execute('SELECT * FROM loans WHERE loan_account_number = ?', (loan_account_number,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Loan with account number {loan_account_number} not found.")
    loan = Loan(
        loan_account_number=row[1],
        sanctioned_amount=row[2],
        disbursed_amount=row[2],  # Not stored separately in DB schema
        interest_start_date=datetime.fromisoformat(row[3]).date(),
        emi_start_date=datetime.fromisoformat(row[4]).date(),
        interest_rate=row[5],
        tenure_months=row[6],
        emi_amount=row[7],
        is_fully_disbursed=bool(row[8])
    )
    # Load prepayments
    c.execute('SELECT date, amount, note FROM prepayments WHERE loan_id = ? ORDER BY date', (row[0],))
    prepayments = [Prepayment(date=datetime.fromisoformat(r[0]).date(), amount=r[1], note=r[2]) for r in c.fetchall()]
    # Load amortization schedule
    c.execute('''
        SELECT installment_num, emi_due_date, opening_principal, emi_amount, principal_component, interest_component, closing_principal, applicable_interest_rate, total_amount_due
        FROM amortization_schedule WHERE loan_id = ? ORDER BY installment_num
    ''', (row[0],))
    schedule = [AmortizationRow(
        installment_num=r[0],
        emi_due_date=datetime.fromisoformat(r[1]).date(),
        opening_principal=r[2],
        emi_amount=r[3],
        principal_component=r[4],
        interest_component=r[5],
        closing_principal=r[6],
        applicable_interest_rate=r[7],
        total_amount_due=r[8]
    ) for r in c.fetchall()]
    conn.close()
    return loan, prepayments, schedule

def save_disbursements_to_db(loan_account_number: str, disbursements: List[Disbursement]):
    """
    Save disbursements for a loan to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    loan_id = c.execute('SELECT id FROM loans WHERE loan_account_number = ?', (loan_account_number,)).fetchone()[0]
    c.execute('DELETE FROM disbursements WHERE loan_id = ?', (loan_id,))
    for d in disbursements:
        c.execute('''
            INSERT INTO disbursements (loan_id, date, amount, note) VALUES (?, ?, ?, ?)
        ''', (loan_id, d.date.isoformat(), d.amount, d.note))
    conn.commit()
    conn.close()
    print(f"Disbursements saved for loan {loan_account_number}")

def load_disbursements_from_db(loan_account_number: str) -> List[Disbursement]:
    """
    Load disbursements for a loan from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    loan_id = c.execute('SELECT id FROM loans WHERE loan_account_number = ?', (loan_account_number,)).fetchone()[0]
    c.execute('SELECT date, amount, note FROM disbursements WHERE loan_id = ? ORDER BY date', (loan_id,))
    disbursements = [Disbursement(date=datetime.fromisoformat(r[0]).date(), amount=r[1], note=r[2]) for r in c.fetchall()]
    conn.close()
    return disbursements

def save_rate_changes_to_db(loan_account_number: str, rate_changes: List[RateChange]):
    """
    Save interest rate changes for a loan to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    loan_id = c.execute('SELECT id FROM loans WHERE loan_account_number = ?', (loan_account_number,)).fetchone()[0]
    # Use a new table for rate changes if not already present
    c.execute('''CREATE TABLE IF NOT EXISTS rate_changes (
        id INTEGER PRIMARY KEY,
        loan_id INTEGER,
        date DATE,
        new_rate REAL,
        note TEXT,
        FOREIGN KEY (loan_id) REFERENCES loans(id)
    )''')
    c.execute('DELETE FROM rate_changes WHERE loan_id = ?', (loan_id,))
    for rc in rate_changes:
        c.execute('''
            INSERT INTO rate_changes (loan_id, date, new_rate, note) VALUES (?, ?, ?, ?)
        ''', (loan_id, rc.date.isoformat(), rc.new_rate, rc.note))
    conn.commit()
    conn.close()
    print(f"Rate changes saved for loan {loan_account_number}")

def load_rate_changes_from_db(loan_account_number: str) -> List[RateChange]:
    """
    Load interest rate changes for a loan from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    loan_id = c.execute('SELECT id FROM loans WHERE loan_account_number = ?', (loan_account_number,)).fetchone()[0]
    c.execute('''CREATE TABLE IF NOT EXISTS rate_changes (
        id INTEGER PRIMARY KEY,
        loan_id INTEGER,
        date DATE,
        new_rate REAL,
        note TEXT,
        FOREIGN KEY (loan_id) REFERENCES loans(id)
    )''')
    c.execute('SELECT date, new_rate, note FROM rate_changes WHERE loan_id = ? ORDER BY date', (loan_id,))
    rate_changes = [RateChange(date=datetime.fromisoformat(r[0]).date(), new_rate=r[1], note=r[2]) for r in c.fetchall()]
    conn.close()
    return rate_changes

if __name__ == "__main__":
    # Example usage of the Loan and amortization logic
    loan = Loan(
        loan_account_number="LN001",  # Example loan account number
        sanctioned_amount=5000000,     # Example sanctioned amount
        disbursed_amount=5000000,      # Example disbursed amount
        interest_start_date=date(2025, 7, 1),  # Interest calculation start date
        emi_start_date=date(2025, 8, 1),       # EMI payment start date
        interest_rate=8.5,             # Annual interest rate
        tenure_months=240,             # Tenure in months (20 years)
        emi_amount=0,                  # Will be calculated below
        is_fully_disbursed=True        # Assume fully disbursed for this example
    )
    # Calculate EMI for the loan
    loan.emi_amount = calculate_emi(loan.sanctioned_amount, loan.interest_rate, loan.tenure_months)
    # Generate the amortization schedule
    schedule = generate_amortization_schedule(
        principal=loan.sanctioned_amount,
        annual_rate=loan.interest_rate,
        tenure_months=loan.tenure_months,
        start_date=loan.emi_start_date
    )
    # Print the first 3 rows of the amortization schedule as a sample
    for row in schedule[:3]:
        print(row)

    # Example prepayments
    prepayments = [
        Prepayment(date=date(2026, 1, 1), amount=500000, note="Year-end bonus prepayment"),
        Prepayment(date=date(2026, 6, 1), amount=1000000, note="Lump sum prepayment"),
    ]
    # Generate schedule with prepayments
    schedule_with_prepayments = generate_amortization_schedule_with_prepayments(
        principal=loan.sanctioned_amount,
        annual_rate=loan.interest_rate,
        tenure_months=loan.tenure_months,
        start_date=loan.emi_start_date,
        prepayments=prepayments,
        is_fully_disbursed=loan.is_fully_disbursed
    )
    # Print the schedule with prepayments
    print("\nAmortization Schedule with Prepayments:")
    for row in schedule_with_prepayments:
        print(row)

    print("\nSummary for Standard Schedule:")
    print_summary_statistics(schedule)
    export_schedule_to_csv(schedule, "standard_amortization_schedule.csv")

    print("\nSummary for Schedule with Prepayments:")
    print_summary_statistics(schedule_with_prepayments)
    export_schedule_to_csv(schedule_with_prepayments, "amortization_with_prepayments.csv")

    # Save to DB
    save_loan_to_db(loan, prepayments, schedule_with_prepayments)

    # Load from DB (for verification)
    loaded_loan, loaded_prepayments, loaded_schedule = load_loan_from_db("LN001")
    print("\nLoaded Loan:", loaded_loan)
    print("Loaded Prepayments:", loaded_prepayments)
    print("Loaded Schedule (first 3 rows):")
    for row in loaded_schedule[:3]:
        print(row)

    # Example disbursements
    disbursements = [
        Disbursement(date=date(2025, 7, 15), amount=2500000, note="Initial disbursement"),
        Disbursement(date=date(2026, 1, 15), amount=2500000, note="Second disbursement"),
    ]
    # Save disbursements to DB
    save_disbursements_to_db(loan.loan_account_number, disbursements)

    # Load disbursements from DB
    loaded_disbursements = load_disbursements_from_db(loan.loan_account_number)
    print("Loaded Disbursements:", loaded_disbursements)

    # Example rate changes
    rate_changes = [
        RateChange(date=date(2026, 8, 1), new_rate=9.0, note="Rate hike"),
        RateChange(date=date(2027, 8, 1), new_rate=8.75, note="Rate cut"),
    ]
    # Save rate changes to DB
    save_rate_changes_to_db(loan.loan_account_number, rate_changes)

    # Load rate changes from DB
    loaded_rate_changes = load_rate_changes_from_db(loan.loan_account_number)
    print("Loaded Rate Changes:", loaded_rate_changes)
