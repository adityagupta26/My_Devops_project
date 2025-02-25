import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Configuration: List of global market indices
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

# Function to fetch index data
def fetch_index_data(index_symbol, start_date='2000-01-01', end_date='2025-01-01'):
    """Fetch historical data for the given index symbol using Yahoo Finance."""
    try:
        data = yf.download(index_symbol, start=start_date, end=end_date)
        data['Index'] = index_symbol  # Add the index symbol as a column
        return data
    except Exception as e:
        print(f"Error fetching data for {index_symbol}: {str(e)}")
        return None

# Function to track index performance
def track_indices(indices, start_date='2000-01-01', end_date='2025-01-01'):
    """Fetch and concatenate data for multiple indices."""
    all_data = []
    for index_name, index_symbol in indices.items():
        print(f"Fetching data for {index_name} ({index_symbol})...")
        index_data = fetch_index_data(index_symbol, start_date, end_date)
        if index_data is not None:
            all_data.append(index_data)
    
    # Concatenate all the data into a single DataFrame
    return pd.concat(all_data)

# Function to calculate percentage change
def calculate_returns(df):
    """Calculate daily returns for each index."""
    df['Daily Return'] = df['Adj Close'].pct_change() * 100
    return df

# Function to plot index performance
def plot_performance(df):
    """Plot the performance of each index."""
    df_grouped = df.groupby('Index').last()  # Get the last data point for each index
    df_grouped = df_grouped['Adj Close'].sort_values(ascending=False)
    
    df_grouped.plot(kind='bar', figsize=(10, 6), title="Global Market Index Performance (Latest)")
    plt.ylabel('Index Value')
    plt.show()

# Function to save index data to CSV
def save_data(df, filename='global_index_data.csv'):
    """Save the collected index data to a CSV file."""
    df.to_csv(filename)
    print(f"Data saved to {filename}")

# Main function
def main():
    # Fetch and track index data
    print("Collecting global market index data...")
    df = track_indices(indices)

    # Calculate returns
    print("Calculating daily returns...")
    df_with_returns = calculate_returns(df)

    # Save the data to a CSV file
    save_data(df_with_returns)

    # Plot the performance
    print("Plotting the global market index performance...")
    plot_performance(df_with_returns)

    # Optionally: track weekly or monthly returns, visualize trends, etc.
    # You can extend this functionality with further analysis, e.g., weekly/monthly returns, volatility, etc.

if __name__ == "__main__":
    main()
