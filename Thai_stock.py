import os
import yfinance as yf
import pandas as pd

# Thai SET stocks (.BK suffix)
tickers = ["PTT.BK", "AOT.BK", "CPALL.BK", "KBANK.BK",'TACC.BK']

# Create output folder in the current working directory
output_folder = os.path.join(os.getcwd(), "Thai_stock_data")
os.makedirs(output_folder, exist_ok=True)

# Download 15-minute data (Yahoo generally allows up to the latest 60 days)
data = yf.download(
    tickers=tickers,
    period="5d",
    interval="5m",
    group_by="ticker",
    auto_adjust=False,
    progress=False,
    threads=True
)

# Save one CSV file per stock
for ticker in tickers:
    try:
        stock_df = data[ticker].copy()

        # Skip if Yahoo returned no data
        if stock_df.empty or stock_df.dropna(how="all").empty:
            print(f"No data found for {ticker}")
            continue

        # Remove rows with no price data
        stock_df = stock_df.dropna(how="all")

        # Filename example: Thai_stock_data/PTT_BK_15min.csv
        filename = f"{ticker.replace('.', '_')}.csv"
        filepath = os.path.join(output_folder, filename)

        stock_df.to_csv(filepath, index=True)
        print(f"Saved: {filepath}")

    except KeyError:
        print(f"Could not process: {ticker}")