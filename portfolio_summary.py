import pandas as pd

# Portfolio data (replace with dynamic fetch if needed)
equity_data = [
    {"Symbol": "EEL130826", "Exchange": "BSE", "Qty": 10, "Last Price": 106950, "Avg Price": 0, "PnL": 1069500},
    {"Symbol": "GAIL", "Exchange": "NSE", "Qty": 500, "Last Price": 191.28, "Avg Price": 103.72, "PnL": 43780},
    {"Symbol": "GMRAIRPORT", "Exchange": "BSE", "Qty": 500, "Last Price": 86.83, "Avg Price": 90.63, "PnL": -1900},
    {"Symbol": "HDFCBANK", "Exchange": "BSE", "Qty": 80, "Last Price": 1933.55, "Avg Price": 1385.42, "PnL": 43850.5},
    {"Symbol": "ICICIBANK", "Exchange": "NSE", "Qty": 100, "Last Price": 1449.8, "Avg Price": 703.03, "PnL": 74677.5},
    {"Symbol": "INFY", "Exchange": "BSE", "Qty": 50, "Last Price": 1564.5, "Avg Price": 1399.49, "PnL": 8250.5},
    {"Symbol": "IOC", "Exchange": "BSE", "Qty": 500, "Last Price": 144.1, "Avg Price": 66.65, "PnL": 38725},
    {"Symbol": "MOSCHIP", "Exchange": "BSE", "Qty": 150, "Last Price": 177.15, "Avg Price": 235.15, "PnL": -8700},
    {"Symbol": "MOTHERSON", "Exchange": "NSE", "Qty": 1000, "Last Price": 148.23, "Avg Price": 74.30, "PnL": 73932.5},
    {"Symbol": "MSUMI", "Exchange": "BSE", "Qty": 750, "Last Price": 58.15, "Avg Price": 50.2, "PnL": 5962.5},
    {"Symbol": "PFC", "Exchange": "BSE", "Qty": 650, "Last Price": 405.85, "Avg Price": 101.52, "PnL": 197817.5},
    {"Symbol": "POWERGRID", "Exchange": "BSE", "Qty": 250, "Last Price": 298.05, "Avg Price": 180.41, "PnL": 29410},
    {"Symbol": "PROTEAN", "Exchange": "BSE", "Qty": 55, "Last Price": 976.55, "Avg Price": 1247.27, "PnL": -14889.75},
    {"Symbol": "REDINGTON", "Exchange": "NSE", "Qty": 200, "Last Price": 271.77, "Avg Price": 183.87, "PnL": 17580},
    {"Symbol": "TATACONSUM", "Exchange": "NSE", "Qty": 44, "Last Price": 1140.8, "Avg Price": 677.70, "PnL": 20376.53},
    {"Symbol": "TATAMOTORS", "Exchange": "BSE", "Qty": 150, "Last Price": 718.15, "Avg Price": 399, "PnL": 47872.5},
]

mf_data = [
    {"Fund": "DSP TIGER FUND - DIRECT PLAN", "Qty": 1260.431, "Last Price": 52.39, "Avg Price": 52.76},
    {"Fund": "HDFC LARGE AND MID CAP FUND - DIRECT PLAN", "Qty": 1209.61, "Last Price": 46.977, "Avg Price": 46.71},
    {"Fund": "MIRAE ASSET NIFTY 50 INDEX FUND - DIRECT PLAN", "Qty": 4122.013, "Last Price": 10.1443, "Avg Price": 9.70},
]

def equity_summary(df):
    df["Current Value"] = df["Qty"] * df["Last Price"]
    df["Invested Value"] = df["Qty"] * df["Avg Price"]
    df["Gain/Loss"] = df["Current Value"] - df["Invested Value"]
    return df

def mf_summary(df):
    df["Current Value"] = df["Qty"] * df["Last Price"]
    df["Invested Value"] = df["Qty"] * df["Avg Price"]
    df["Gain/Loss"] = df["Current Value"] - df["Invested Value"]
    return df

def main():
    eq_df = pd.DataFrame(equity_data)
    mf_df = pd.DataFrame(mf_data)
    eq_df = equity_summary(eq_df)
    mf_df = mf_summary(mf_df)
    print("Equity Portfolio Summary:\n", eq_df[["Symbol", "Exchange", "Qty", "Current Value", "Invested Value", "Gain/Loss"]])
    print("\nMutual Fund Portfolio Summary:\n", mf_df[["Fund", "Qty", "Current Value", "Invested Value", "Gain/Loss"]])
    networth = eq_df["Current Value"].sum() + mf_df["Current Value"].sum()
    total_gain = eq_df["Gain/Loss"].sum() + mf_df["Gain/Loss"].sum()
    print(f"\nTotal Networth: ₹{networth:,.2f}")
    print(f"Total Gain/Loss: ₹{total_gain:,.2f}")

if __name__ == "__main__":
    main()
