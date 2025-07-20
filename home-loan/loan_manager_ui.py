import streamlit as st
from datetime import date, datetime
from loan_calculator import (
    Loan, Prepayment, Disbursement, RateChange, calculate_emi, generate_amortization_schedule_with_prepayments,
    save_loan_to_db, load_loan_from_db, save_disbursements_to_db, load_disbursements_from_db,
    save_rate_changes_to_db, load_rate_changes_from_db
)
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "home_loan.db"

def get_all_loans():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT loan_account_number FROM loans')
    loans = [row[0] for row in c.fetchall()]
    conn.close()
    return loans

def delete_loan(loan_account_number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM loans WHERE loan_account_number = ?', (loan_account_number,))
    c.execute('DELETE FROM prepayments WHERE loan_id NOT IN (SELECT id FROM loans)')
    c.execute('DELETE FROM amortization_schedule WHERE loan_id NOT IN (SELECT id FROM loans)')
    c.execute('DELETE FROM disbursements WHERE loan_id NOT IN (SELECT id FROM loans)')
    c.execute('DELETE FROM rate_changes WHERE loan_id NOT IN (SELECT id FROM loans)')
    conn.commit()
    conn.close()

st.title("Home Loan Manager")

menu = st.sidebar.selectbox("Choose Action", [
    "Add Loan", "View/Update Loan", "Delete Loan", "Add Disbursement", "Add Prepayment", "Change Interest Rate"
])

if menu == "Add Loan":
    st.header("Add New Loan Account")
    loan_account_number = st.text_input("Loan Account Number")
    sanctioned_amount = st.number_input("Sanctioned Amount", min_value=0.0)
    disbursed_amount = st.number_input("Disbursed Amount", min_value=0.0)
    interest_start_date = st.date_input("Interest Start Date", value=date.today())
    emi_start_date = st.date_input("EMI Start Date", value=date.today())
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
    tenure_months = st.number_input("Tenure (months)", min_value=1, step=1)
    is_fully_disbursed = st.checkbox("Is Fully Disbursed?", value=True)
    if st.button("Add Loan"):
        loan = Loan(
            loan_account_number=loan_account_number,
            sanctioned_amount=sanctioned_amount,
            disbursed_amount=disbursed_amount,
            interest_start_date=interest_start_date,
            emi_start_date=emi_start_date,
            interest_rate=interest_rate,
            tenure_months=tenure_months,
            emi_amount=0,
            is_fully_disbursed=is_fully_disbursed
        )
        loan.emi_amount = calculate_emi(sanctioned_amount, interest_rate, tenure_months)
        save_loan_to_db(loan, [], [])
        st.success("Loan added successfully!")

elif menu == "View/Update Loan":
    st.header("View or Update Loan")
    loans = get_all_loans()
    selected_loan = st.selectbox("Select Loan Account", loans)
    if selected_loan:
        loan, prepayments, schedule = load_loan_from_db(selected_loan)
        st.write(loan)
        st.write("Prepayments:", prepayments)
        st.write("Schedule (first 5 rows):", schedule[:5])
        # Update fields
        if st.button("Update Loan Info"):
            # For simplicity, not implementing update fields UI here
            st.info("Update feature coming soon!")

elif menu == "Delete Loan":
    st.header("Delete Loan Account")
    loans = get_all_loans()
    selected_loan = st.selectbox("Select Loan Account to Delete", loans)
    if st.button("Delete Loan"):
        delete_loan(selected_loan)
        st.success("Loan deleted successfully!")

elif menu == "Add Disbursement":
    st.header("Add Disbursement to Loan")
    loans = get_all_loans()
    selected_loan = st.selectbox("Select Loan Account", loans)
    if selected_loan:
        disb_date = st.date_input("Disbursement Date", value=date.today())
        disb_amount = st.number_input("Disbursement Amount", min_value=0.0)
        note = st.text_input("Note")
        if st.button("Add Disbursement"):
            disbursements = load_disbursements_from_db(selected_loan)
            disbursements.append(Disbursement(date=disb_date, amount=disb_amount, note=note))
            save_disbursements_to_db(selected_loan, disbursements)
            st.success("Disbursement added!")
        st.write("Current Disbursements:")
        st.write(load_disbursements_from_db(selected_loan))

elif menu == "Add Prepayment":
    st.header("Add Prepayment to Loan")
    loans = get_all_loans()
    selected_loan = st.selectbox("Select Loan Account", loans)
    if selected_loan:
        prepay_date = st.date_input("Prepayment Date", value=date.today())
        prepay_amount = st.number_input("Prepayment Amount", min_value=0.0)
        note = st.text_input("Note")
        if st.button("Add Prepayment"):
            loan, prepayments, _ = load_loan_from_db(selected_loan)
            prepayments.append(Prepayment(date=prepay_date, amount=prepay_amount, note=note))
            schedule = generate_amortization_schedule_with_prepayments(
                principal=loan.sanctioned_amount,
                annual_rate=loan.interest_rate,
                tenure_months=loan.tenure_months,
                start_date=loan.emi_start_date,
                prepayments=prepayments,
                is_fully_disbursed=loan.is_fully_disbursed
            )
            save_loan_to_db(loan, prepayments, schedule)
            st.success("Prepayment added and schedule updated!")

elif menu == "Change Interest Rate":
    st.header("Change Interest Rate for Loan")
    loans = get_all_loans()
    selected_loan = st.selectbox("Select Loan Account", loans)
    if selected_loan:
        rate_date = st.date_input("Effective Date", value=date.today())
        new_rate = st.number_input("New Interest Rate (%)", min_value=0.0)
        note = st.text_input("Note")
        if st.button("Add Rate Change"):
            rate_changes = load_rate_changes_from_db(selected_loan)
            rate_changes.append(RateChange(date=rate_date, new_rate=new_rate, note=note))
            save_rate_changes_to_db(selected_loan, rate_changes)
            st.success("Rate change added!")
        st.write("Current Rate Changes:")
        st.write(load_rate_changes_from_db(selected_loan))
