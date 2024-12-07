# This file contains the code to calculate the maturity amount of PPF account with SIP investment appraoch.
# The calculate_sip function calculates the maturity amount of PPF account with monthly SIP investment approach.
# The calculate_sip function takes starting principal, sip amount, interest rate as input and returns the maturity 
# amount of PPF account with SIP investment approach.

# There is a second method calculate_sip_full that calculates the maturity amount of PPF account with sip investment approach, for full
# duration of the investment. This method does not take any parameters, and will return a data frame with columns Year, Contribution, 
# Interest and Balance. Internally it will call calculate_sip for every year of the investment and calculate the maturity amount. 


import pandas as pd

def calculate_interest(principal, days, interest_rate):
    if days == 365:
        days_in_year = 365
    else:
        days_in_year = 365
    return principal * interest_rate * (days / days_in_year)


def calculate_sip(starting_principal, sip_amount, interest_rate):
    balance = starting_principal
    monthly_contribution = sip_amount

    for month in range(12):
        principal = monthly_contribution
        year_contribution += principal
        balance += principal

        # Interest for remaining days in the year
        days_remaining = 365 - (30 * month)
        interest = calculate_interest(principal, days_remaining, interest_rate)
        year_interest += interest

    return balance, interest