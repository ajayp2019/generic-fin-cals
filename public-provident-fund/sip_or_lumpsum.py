import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

# PPF Parameters
interest_rate = 8.1 / 100  # Annual interest rate
annual_investment = 150000  # Annual contribution limit
investment_years = 15 + (5 * 2)  # Duration in years (15 years + 2 extensions of 5 years each)
start_date = date(2024, 4, 1)  # Start date of investment

# Function to calculate interest for a given principal and days
def calculate_interest(principal, days):
    """
    Calculate the interest earned on a principal amount over a given number of days.

    Args:
        principal (float): The principal amount of money.
        days (int): The number of days the money is invested or borrowed for.

    Returns:
        float: The interest earned on the principal amount over the specified number of days.
    """
    # Check if the year is a leap year
    year = start_date.year + (days // 365)
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_year = 366
    else:
        days_in_year = 365
    return principal * interest_rate * (days / days_in_year)

# Function to calculate PPF maturity with lump sum

def calculate_lumpsum():
    balance = 0
    contributions = []
    interests = []
    balances = []

    for year in range(investment_years):
        principal = annual_investment
        balance += principal
        contributions.append(principal)

        # Interest for the year
        interest = calculate_interest(balance, 365)
        balance += interest
        interests.append(interest)
        balances.append(balance)

    return pd.DataFrame({"Year": range(1, investment_years + 1),
                         "Contribution": contributions,
                         "Interest": interests,
                         "Balance": balances})

# Function to calculate PPF maturity with monthly SIP

def calculate_sip():
    balance = 0
    monthly_contribution = annual_investment / 12
    contributions = []
    interests = []
    balances = []

    for year in range(investment_years):
        year_contribution = 0
        year_interest = 0

        for month in range(12):
            principal = monthly_contribution
            year_contribution += principal
            balance += principal

            # Interest for remaining days in the year
            days_remaining = 365 - (30 * month)
            interest = calculate_interest(principal, days_remaining)
            year_interest += interest

        balance += year_interest
        contributions.append(year_contribution)
        interests.append(year_interest)
        balances.append(balance)

    return pd.DataFrame({"Year": range(1, investment_years + 1),
                         "Contribution": contributions,
                         "Interest": interests,
                         "Balance": balances})

# Calculate results
lumpsum_df = calculate_lumpsum()
sip_df = calculate_sip()

# Combine results for comparison
comparison_df = pd.DataFrame({
    "Year": lumpsum_df["Year"],
    "Lumpsum_Balance": lumpsum_df["Balance"],
    "SIP_Balance": sip_df["Balance"],
    "Difference": sip_df["Balance"] - lumpsum_df["Balance"]
})

# Print results
print("PPF Lump Sum Investment:")
print(lumpsum_df)
print("\nPPF SIP Investment:")
print(sip_df)

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(comparison_df["Year"], comparison_df["Lumpsum_Balance"], label="Lump Sum Investment", marker="o")
plt.plot(comparison_df["Year"], comparison_df["SIP_Balance"], label="SIP Investment", marker="s")
plt.xlabel("Year")
plt.ylabel("Balance (₹)")
plt.title("PPF Lump Sum vs SIP Investment Comparison")
plt.legend()
plt.grid(True)
plt.show()
