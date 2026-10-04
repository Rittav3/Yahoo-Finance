import os
import yfinance as yf
import pandas as pd
import mplfinance as mpf

# Thai SET stocks (.BK suffix)
tickers = ["PTT.BK", "AOT.BK", "CPALL.BK", "KBANK.BK"]

# Select ticker to plot
selected_ticker = "KBANK.BK" # to plot graph

# Create output folder in the current working directory
output_folder = os.path.join(os.getcwd(), "Thai15min")
os.makedirs(output_folder, exist_ok=True)

# Download 15-minute data
data = yf.download(
    tickers=tickers,
    period="60d",
    interval="15m",
    group_by="ticker",
    auto_adjust=False,
    progress=False,
    threads=True
)

# Save one CSV per ticker
for ticker in tickers:
    try:
        stock_df = data[ticker].copy().dropna(how="all")

        if stock_df.empty:
            print(f"No data found for {ticker}")
            continue

        filename = f"{ticker.replace('.', '_')}_15min.csv"
        filepath = os.path.join(output_folder, filename)

        stock_df.to_csv(filepath)
        print(f"Saved: {filepath}")

    except KeyError:
        print(f"Could not process: {ticker}")

# Plot selected ticker OHLC / candlestick chart
try:
    plot_df = data[selected_ticker].copy().dropna(how="all")

    if plot_df.empty:
        print(f"No data available to plot for {selected_ticker}")
    else:
        # Plot latest 100 fifteen-minute candles
        plot_df = plot_df.tail(100)

        # Optional moving averages
        mpf.plot(
            plot_df,
            type="candle",
            style="yahoo",
            title=f"{selected_ticker} - 15 Minute OHLC",
            ylabel="Price (THB)",
            volume=True,
            mav=(10, 20),
            figsize=(14, 8)
        )

except KeyError:
    print(f"Ticker {selected_ticker} was not found.")