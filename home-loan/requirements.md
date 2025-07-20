# Home Loan Amortization Calculator Requirements

## Amortization Table Columns
- Installment Num
- EMI Due Date
- Opening Principal
- EMI Amount
- Principal Component of the EMI
- Interest component of the EMI
- Closing Principal
- Applicable Rate of Interest (%)
- Total Amount Due (future EMIs)

## Additional Requirements for Pre-payments
- Maintain a record of all part pre-payments made during the loan tenure.
- If the loan is not fully disbursed, part pre-payments should reduce the EMI amount.
- Once the loan is fully disbursed, part pre-payments should reduce the tenure (number of installments), not the EMI amount.
- The amortization schedule should reflect the impact of pre-payments on EMI or tenure as applicable.

## EMI Payment Records
- Maintain a record for each EMI payment:
  - Installment number
  - Scheduled due date
  - Actual payment date (nullable if not yet paid)
  - Amount paid
  - Status (e.g., Paid, Missed, Partial, Upcoming)
  - Note (optional)
- Link EMI payment records to each loan and cross-reference with the amortization schedule for transparency and reporting.

## Data Persistence and Multi-Loan Support
- All loan and transaction information should be persisted for future reference (e.g., using files or a database).
- The system should support viewing and managing multiple loans.
- For each loan, maintain:
  - Sanctioned amount (full loan amount; loan is not fully disbursed until disbursed amount equals sanctioned amount; this affects pre-payment impact)
  - Interest start date (when interest calculation begins)
  - Loan account number (unique identifier for each loan)

## What-if Scenario Simulation
- Allow users to simulate different payment scenarios (e.g., extra pre-payments, missed EMIs, changes in interest rate, etc.) without affecting actual loan records.
- Support saving, viewing, and comparing multiple simulation runs for each loan.
- Simulations should leverage the same data model and logic as real data, but be clearly separated from actual records.

## Data Persistence
- Use a persistent SQLite database to store all loan, payment, prepayment, disbursement, and simulation data.

## User Interface
- Provide a user-friendly interface for data entry, loan management, and running simulations.
- Support web-based UI using Gradio or Streamlit for:
  - Adding and editing loan details
  - Recording disbursements, prepayments, and EMI payments
  - Viewing and exporting amortization schedules
  - Running and comparing "what-if" simulations interactively

## Next Steps
- Define input parameters (loan amount, interest rate, tenure, start date, etc.)
- Implement EMI calculation logic
- Generate amortization schedule as per above columns
- Output as table (console, CSV, or web UI)
