import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Enhanced Global Indices list with regions
indices = {
    # North America
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'Dow Jones': '^DJI',
    'TSX Composite': '^GSPTSE',
    
    # Europe
    'FTSE 100': '^FTSE',
    'DAX': '^GDAXI',
    'CAC 40': '^FCHI',
    'Euro Stoxx 50': '^STOXX50E',
    
    # Asia-Pacific
    'Nikkei 225': '^N225',
    'Hang Seng': '^HSI',
    'ASX 200': '^AXJO',
    'Nifty 50': '^NSEI',
    
    # Emerging Markets
    'Bovespa': '^BVSP',
    'MOEX Russia': 'IMOEX.ME',
    'Shanghai Composite': '000001.SS'
}

# Technical Analysis Parameters
TA_CONFIG = {
    'rsi_period': 14,
    'ma_periods': [50, 200],
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bollinger_period': 20,
    'bollinger_std': 2
}

# Scoring Weights
SCORE_WEIGHTS = {
    'momentum': 0.35,
    'trend': 0.30,
    'volatility': 0.20,
    'volume': 0.15
}

def fetch_index_data(index_symbol, start_date='2020-01-01', end_date=None):
    """Enhanced data fetcher with caching and validation"""
    try:
        data = yf.download(
            index_symbol, 
            start=start_date, 
            end=end_date,
            progress=False,
            auto_adjust=True  # Use adjusted prices automatically
        )
        
        if data.empty:
            raise ValueError("No data returned")
            
        # Add technical columns
        data['Index'] = index_symbol
        data['Daily Return'] = data['Close'].pct_change() * 100
        data = calculate_technical_indicators(data)
        
        return data.dropna()
        
    except Exception as e:
        print(f"Error fetching {index_symbol}: {str(e)}")
        return None

def calculate_technical_indicators(data):
    """Calculate multiple technical indicators"""
    # RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    data['RSI'] = 100 - (100 / (1 + gain.rolling(TA_CONFIG['rsi_period']).mean() / 
                               loss.rolling(TA_CONFIG['rsi_period']).mean()))
    
    # Moving Averages
    for period in TA_CONFIG['ma_periods']:
        data[f'MA{period}'] = data['Close'].rolling(period).mean()
    
    # MACD
    ema12 = data['Close'].ewm(span=TA_CONFIG['macd_fast'], adjust=False).mean()
    ema26 = data['Close'].ewm(span=TA_CONFIG['macd_slow'], adjust=False).mean()
    data['MACD'] = ema12 - ema26
    data['MACD_Signal'] = data['MACD'].ewm(span=TA_CONFIG['macd_signal'], adjust=False).mean()
    
    # Bollinger Bands
    sma = data['Close'].rolling(TA_CONFIG['bollinger_period']).mean()
    std = data['Close'].rolling(TA_CONFIG['bollinger_period']).std()
    data['Bollinger_Upper'] = sma + (std * TA_CONFIG['bollinger_std'])
    data['Bollinger_Lower'] = sma - (std * TA_CONFIG['bollinger_std'])
    
    return data

def calculate_score(data):
    """Enhanced scoring system with multiple factors"""
    if data is None or len(data) < 100:
        return 0
    
    # Normalize metrics
    scaler = MinMaxScaler()
    
    # Momentum Factor (RSI + MACD)
    momentum = (
        0.7 * (data['RSI'].iloc[-1] / 100) + 
        0.3 * (data['MACD'].iloc[-1] / data['Close'].iloc[-1])
    )
    
    # Trend Factor (MA crossover + Bollinger position)
    trend = (
        0.5 * (data['Close'].iloc[-1] / data['MA50'].iloc[-1]) +
        0.5 * (data['Close'].iloc[-1] - data['Bollinger_Lower'].iloc[-1]) / 
               (data['Bollinger_Upper'].iloc[-1] - data['Bollinger_Lower'].iloc[-1])
    )
    
    # Volatility Factor (inverse of 30-day volatility)
    volatility = 1 / (1 + data['Close'].pct_change().rolling(30).std().iloc[-1])
    
    # Volume Factor (recent volume vs average)
    volume = data['Volume'].iloc[-30:].mean() / data['Volume'].iloc[-1]
    
    # Combine scores
    factors = {
        'momentum': momentum,
        'trend': trend,
        'volatility': volatility,
        'volume': volume
    }
    
    # Apply weights and normalize
    weighted_scores = [factors[k] * SCORE_WEIGHTS[k] for k in SCORE_WEIGHTS]
    final_score = sum(weighted_scores)
    
    # Reshape the final score to a 2D array (1 row, 1 column)
    final_score_reshaped = np.array([[final_score]])
    
    # Normalize the final score using MinMaxScaler
    return scaler.fit_transform(final_score_reshaped)[0][0]

def analyze_indices():
    """Main analysis function with enhanced visualization"""
    results = []
    
    for index_name, symbol in indices.items():
        print(f"Analyzing {index_name}...")
        data = fetch_index_data(symbol)
        if data is not None:
            score = calculate_score(data)
            results.append((index_name, score, data))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Display top 5 indices
    print("\n=== Top 5 Indices ===")
    for idx, (name, score, data) in enumerate(results[:5], 1):
        print(f"{idx}. {name}: {score:.2f}")
        
        # Plot technical indicators
        plt.figure(figsize=(12, 6))
        plt.title(f"{name} Technical Analysis")
        
        # Price and Moving Averages
        plt.subplot(2, 1, 1)
        plt.plot(data['Close'], label='Price')
        for period in TA_CONFIG['ma_periods']:
            plt.plot(data[f'MA{period}'], label=f'MA{period}')
        plt.plot(data['Bollinger_Upper'], linestyle='--', color='red', alpha=0.5)
        plt.plot(data['Bollinger_Lower'], linestyle='--', color='green', alpha=0.5)
        plt.ylabel('Price')
        plt.legend()
        
        # RSI and MACD
        plt.subplot(2, 1, 2)
        plt.plot(data['RSI'], label='RSI', color='purple')
        plt.plot(data['MACD'], label='MACD', color='orange')
        plt.plot(data['MACD_Signal'], label='Signal', color='blue')
        plt.axhline(70, linestyle='--', color='red')
        plt.axhline(30, linestyle='--', color='green')
        plt.ylabel('Oscillators')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    return results

if __name__ == "__main__":
    analyze_indices()
