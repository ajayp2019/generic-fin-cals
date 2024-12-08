import pandas as pd
import matplotlib.pyplot as plt

INTEREST_RATE = 7.1/100 # Interest rate for PPF
MAX_TENURE = 15 # Maximum tenure for PPF
EXTN = 5 # Extension period for PPF, allowed for 2 times


def calculate_annual_interest_lumpsum(opening_balance, annual_investment):
    interest = (opening_balance + annual_investment) * INTEREST_RATE
    closing_balance = opening_balance + annual_investment + interest
    return (opening_balance, annual_investment, interest, closing_balance)

def calculate_annual_interest_sip(opening_balance, monthly_sip):
    interest = 0
    ob = opening_balance
    for month in range(12):
        ob += monthly_sip
        interest += ob * INTEREST_RATE/12
    # PPF interest is paid at the end of the year, but calculated for each month based on 
    # the balance at the end of the month.

    closing_balance = opening_balance + monthly_sip*12 + interest
    return (opening_balance, annual_investment, interest, closing_balance)



def calculate_ppf_maturity(investment_years, annual_investment, sip=False, extn=False):
    contributions = []
    interests = []
    balances = []

    assert investment_years <= MAX_TENURE, f"Maximum tenure for PPF is {MAX_TENURE} years."
    assert annual_investment <= 150000, "Annual investment cannot exceed 150,000."

    i = 0
    cb = 0

    if extn:
        investment_years += EXTN*2

    for year in range(investment_years):
        # Interest for the year
        if sip:
            ob, annual_investment, i, cb = calculate_annual_interest_sip(cb, annual_investment/12)
        else: 
            ob, annual_investment, i, cb = calculate_annual_interest_lumpsum(cb, annual_investment)

        contributions.append(annual_investment)
        interests.append(i)
        balances.append(cb)

    df = pd.DataFrame({"Year": range(1, investment_years + 1),
                       "Contribution": contributions,
                       "Interest": interests,
                       "Balance": balances})
    return df


if __name__ == "__main__":
    investment_years = 15
    annual_investment = 150000

    # print a graph showing the growth of the PPF account over the years in SIP and lumpsum investment
    df_lumpsum = calculate_ppf_maturity(investment_years, annual_investment, sip=False, extn=True)
    df_sip = calculate_ppf_maturity(investment_years, annual_investment, sip=True, extn=True)

    plt.figure(figsize=(10, 5))
    # plot the princpal amount, interest and balance for both lumpsum and SIP
    # plt.plot(df_lumpsum['Year'], df_lumpsum['Contribution'], label="Annual Investment")
    plt.plot(df_lumpsum['Year'], df_lumpsum['Balance'], label="Lumpsum Investment")
    plt.plot(df_sip['Year'], df_sip['Balance'], label="Monthly SIP")
    plt.xlabel("Year")
    plt.ylabel("Balance (in Lakhs)")
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x/100000))))
    plt.title("PPF Maturity with Lumpsum Investment and Monthly SIP")
    # Bar plot for annual contribution
    plt.bar(df_lumpsum['Year'], df_lumpsum['Contribution'], label="Principal (Lumpsum)", color='b')

    # Add vertical lines at 15, 20, and 25 years
    for year in [15, 20, 25]:
        plt.axvline(x=year, color='r', linestyle='--', label=f'Year {year}')
    
    # Add horizontal lines to show increment in balance between 15 to 20, and 20 to 25 years
    y_15 = df_lumpsum.loc[df_lumpsum['Year'] == 15, 'Balance'].values[0]
    y_20 = df_lumpsum.loc[df_lumpsum['Year'] == 20, 'Balance'].values[0]
    y_25 = df_lumpsum.loc[df_lumpsum['Year'] == 25, 'Balance'].values[0]
    plt.hlines(y=y_20, xmin=15, xmax=20, colors='g', linestyles='dotted')
    plt.hlines(y=y_25, xmin=20, xmax=25, colors='m', linestyles='dotted')

    plt.text(17.5, y_20, f"{((y_20 - y_15) / 100000):,.2f} Lakhs", horizontalalignment='center', color='g')
    plt.text(22.5, y_25, f"{((y_25 - y_20) / 100000):,.2f} Lakhs", horizontalalignment='center', color='m')

    plt.legend()
    plt.show()

    df_lumpsum['Contribution'] = df_lumpsum['Contribution'].apply(lambda x: f"₹{x:,.2f}")
    df_lumpsum['Interest'] = df_lumpsum['Interest'].apply(lambda x: f"₹{x:,.2f}")
    df_lumpsum['Balance'] = df_lumpsum['Balance'].apply(lambda x: f"₹{x:,.2f}")

    print("PPF Maturity with Lumpsum Investment")
    print(df_lumpsum)

    df_sip['Contribution'] = df_sip['Contribution'].apply(lambda x: f"₹{x:,.2f}")
    df_sip['Interest'] = df_sip['Interest'].apply(lambda x: f"₹{x:,.2f}")
    df_sip['Balance'] = df_sip['Balance'].apply(lambda x: f"₹{x:,.2f}")

    print("\nPPF Maturity with Monthly SIP")
    print(df_sip)
