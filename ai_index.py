import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Global Indices list (we can add more if needed)
indices = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'FTSE 100': '^FTSE',
    'Nikkei 225': '^N225',
    'DAX': '^GDAXI',
    'CAC 40': '^FCHI',
    'Hang Seng': '^HSI',
    'ASX 200': '^AXJO'
}

# Parameters
RSI_PERIOD = 14
MA_PERIOD = 50

# Fetch Index Data Function
def fetch_index_data(index_symbol, start_date='2023-01-01', end_date='2025-01-01'):
    """Fetch historical data for the given index symbol using Yahoo Finance."""
    try:
        data = yf.download(index_symbol, start=start_date, end=end_date)
        data['Index'] = index_symbol  # Add the index symbol as a column
        if 'Adj Close' not in data.columns:
            print(f"Warning: 'Adj Close' column missing for {index_symbol}, using 'Close' instead.")
            data['Adj Close'] = data['Close']  # Fallback to 'Close' if 'Adj Close' is missing
        return data
    except Exception as e:
        print(f"Error fetching data for {index_symbol}: {str(e)}")
        return None

# Calculate RSI (Relative Strength Index)
def calculate_rsi(data, period=RSI_PERIOD):
    """Calculate the Relative Strength Index (RSI) for given data."""
    delta = data['Adj Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Calculate Moving Average (MA)
def calculate_moving_average(data, period=MA_PERIOD):
    """Calculate moving average for given data."""
    return data['Adj Close'].rolling(window=period).mean()

# Calculate Standard Deviation (Volatility)
def calculate_volatility(data):
    """Calculate standard deviation of returns (volatility)."""
    return data['Daily Return'].std()

# Calculate Daily Returns
def calculate_daily_returns(data):
    """Calculate daily returns."""
    data['Daily Return'] = data['Adj Close'].pct_change() * 100
    return data

# Evaluate each index based on the strategy
def evaluate_indices(indices, start_date='2023-01-01', end_date='2025-01-01'):
    scores = []
    for index_name, index_symbol in indices.items():
        print(f"Evaluating {index_name}...")
        data = fetch_index_data(index_symbol, start_date, end_date)
        if data is not None:
            data = calculate_daily_returns(data)
            data['RSI'] = calculate_rsi(data)
            data['MA50'] = calculate_moving_average(data)

            # Calculate momentum: If RSI > 50, consider it bullish momentum
            momentum_score = data['RSI'].iloc[-1] / 100  # RSI score between 0 and 1

            # Calculate trend: If the current price is above the 50-day moving average, it's a bullish trend
            trend_score = 1 if data['Adj Close'].iloc[-1] > data['MA50'].iloc[-1] else 0

            # Calculate volatility: We want to select less volatile indices
            volatility_score = 1 / (1 + calculate_volatility(data))  # Lower volatility = higher score

            # Final score: We combine the momentum, trend, and volatility scores
            final_score = (momentum_score * 0.4) + (trend_score * 0.4) + (volatility_score * 0.2)
            scores.append((index_name, final_score))

    # Sort indices by their final score (higher score means better trade opportunity)
    scores.sort(key=lambda x: x[1], reverse=True)

    return scores

# Main function to get the best indices for today
def suggest_best_indices():
    print("Evaluating indices for the best trading opportunities...")
    scores = evaluate_indices(indices)
    top_2 = scores[:2]  # Select the top 2 indices based on the highest score

    # Display the best 2 trade suggestions
    print("\n=== Best 2 Indices to Trade Today ===")
    for idx, (index_name, score) in enumerate(top_2, 1):
        print(f"{idx}. {index_name} - Score: {score:.4f}")

    # Optionally, you can plot the RSI, MA, and daily returns of these top 2 indices for visualization
    for index_name, _ in top_2:
        data = fetch_index_data(indices[index_name])
        if data is not None:
            data = calculate_daily_returns(data)
            data['RSI'] = calculate_rsi(data)
            data['MA50'] = calculate_moving_average(data)
            data[['RSI', 'Adj Close', 'MA50']].plot(figsize=(10, 6), title=index_name)
            plt.show()

if __name__ == "__main__":
    suggest_best_indices()
