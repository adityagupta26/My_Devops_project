import pandas as pd
import numpy as np
import yfinance as yf
import requests
from sklearn.preprocessing import MinMaxScaler
from pypfopt import EfficientFrontier, objective_functions
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.expected_returns import ema_historical_return

# Configuration
CONFIG = {
    "stock_universe": [
        'MSFT', 'AAPL', 'AMZN', 'GOOGL', 'TSLA', 'NVDA', 'META', 'TSM', 'BRK-B', 'V',
        'UNH', 'JNJ', 'MA', 'HD', 'PG', 'DIS', 'PYPL', 'NFLX', 'INTC', 'VZ', 'INTU', 
        'CSCO', 'PFE', 'MRK', 'ABT', 'NVO', 'CRM', 'MS', 'PEP', 'BA', 'WMT', 'AMD', 
        'BABA', 'TM', 'KO', 'SAP', 'RTX', 'SBUX', 'GS', 'AMGN', 'EXC', 'UNP', 'COP', 
        'XOM', 'CVX', 'LVMUY', 'MCD', 'ISRG', 'LLY', 'BLK', 'T', 'ADBE', 'ATVI', 
        'UPS', 'LOR', 'HMC', 'NTES', 'ASML', 'DHR', 'ZTS', 'GE', 'AON', 'BMY', 
        'ACN', 'NKE', 'TMO', 'LOW', 'FIS', 'FISV', 'ADP', 'MKC', 'CTSH', 'GILD', 
        'NOK', 'ORCL', 'DE', 'CVS', 'AMT', 'COST', 'NTRS', 'SPGI', 'CHTR', 'ABBV', 
        'IBM', 'TXN', 'NKE', 'CME', 'CAT', 'MMM', 'MO', 'PM', 'SYY', 'CLX', 
        'GE', 'TGT', 'SYY', 'REGN', 'MDT', 'ISRG', 'KHC', 'ADSK', 'MCO', 'COF',
        'AXP', 'S&P 500', 'STT', 'DHR', 'EXC', 'EMR', 'LHX', 'MET', 'JPM', 
        'AIG', 'VLO', 'WBA', 'KO', 'CCL', 'XOM', 'GE', 'MCD', 'NKE', 'LOW', 
        'GOOG', 'SCHW', 'ALGN', 'MELI', 'AMT', 'STZ', 'HLT', 'BA', 'CVS', 'GIS',
        'BMY', 'NEM', 'AMAT', 'NFLX', 'WFC', 'NXPI', 'GILD', 'HPE', 'COST'
    ],
    "weights": {
        'revenue_growth': 0.20,
        'profit_margin': 0.15,
        'pe_ratio': 0.10,
        'debt_to_equity': 0.10,
        'dividend_yield': 0.10,
        'rsi': 0.10,
        'esg': 0.25
    },
    "risk_free_rate": 0.04,
    "max_allocation_per_stock": 0.35
}

# Alpha Vantage API (for ESG data)
ALPHA_VANTAGE_API_KEY = 'QPFQFC7FEWQADRXD'  # Register at https://www.alphavantage.co

class StockAnalyzer:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.numeric_cols = [
            'revenue_growth', 'profit_margin', 'pe_ratio',
            'debt_to_equity', 'dividend_yield', 'rsi', 'esg'
        ]
        
    def get_esg_score(self, ticker):
        """Fetch ESG score from Alpha Vantage"""
        try:
            url = f"https://www.alphavantage.co/query?function=ESG_SCORE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url).json()
            return float(response.get('ESG Score', np.nan))
        except Exception as e:
            print(f"ESG Error for {ticker}: {str(e)}")
            return np.nan

    def get_fundamentals(self, ticker):
        """Fetch key financial metrics from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'ticker': ticker,
                'revenue_growth': info.get('revenueGrowth', np.nan),
                'profit_margin': info.get('profitMargins', np.nan),
                'pe_ratio': info.get('trailingPE', np.nan),
                'debt_to_equity': info.get('debtToEquity', np.nan),
                'dividend_yield': info.get('dividendYield', 0) * 100,
                'market_cap': info.get('marketCap', np.nan),
                'industry': info.get('industry', 'N/A')
            }
        except Exception as e:
            print(f"Fundamental Error for {ticker}: {str(e)}")
            return None

    def calculate_rsi(self, ticker, period=14):
        """Calculate Relative Strength Index"""
        try:
            data = yf.download(ticker, period='1y', progress=False)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs)).iloc[-1]
        except Exception as e:
            print(f"RSI Error for {ticker}: {str(e)}")
            return np.nan

    def score_stocks(self, df):
        """Normalize and score stocks with type-safe operations"""
        # Clean data: Drop rows with missing values for critical columns
        df = df.dropna(subset=self.numeric_cols)

        # If no rows left after dropping missing data, return an empty dataframe
        if df.empty:
            print("No valid data left for scoring.")
            return df
        
        # Fill missing values only for numeric columns (use mean to fill)
        df[self.numeric_cols] = df[self.numeric_cols].fillna(
            df[self.numeric_cols].mean()
        )

        # Print the DataFrame for debugging purposes
        print("\nData for Scoring (after cleaning and filling missing values):")
        print(df)

        # Normalization
        positive_metrics = ['revenue_growth', 'profit_margin', 'dividend_yield', 'esg']
        negative_metrics = ['pe_ratio', 'debt_to_equity', 'rsi']

        # Check if there are still valid values for scaling
        for metric in positive_metrics:
            if df[metric].isnull().all():
                print(f"Warning: No valid values for {metric} in the data.")
            else:
                df[f'{metric}_score'] = self.scaler.fit_transform(df[[metric]])
                
        for metric in negative_metrics:
            if df[metric].isnull().all():
                print(f"Warning: No valid values for {metric} in the data.")
            else:
                df[f'{metric}_score'] = 1 - self.scaler.fit_transform(df[[metric]])

        # Calculate weighted score
        weights = CONFIG['weights']
        df['total_score'] = sum(df[f'{metric}_score'] * weight 
                               for metric, weight in weights.items())

        return df.sort_values('total_score', ascending=False).reset_index(drop=True)

    def optimize_portfolio(self, df_top_stocks):
        """Calculate optimal portfolio allocation"""
        try:
            # Get historical returns
            prices = yf.download(list(df_top_stocks['ticker']), period='3y')['Adj Close']
            returns = ema_historical_return(prices)
            
            # Calculate covariance matrix
            cov_matrix = CovarianceShrinkage(prices).ledoit_wolf()
            
            # Optimize portfolio
            ef = EfficientFrontier(returns, cov_matrix)
            ef.add_objective(objective_functions.L2_reg, gamma=0.1)
            ef.max_sharpe(risk_free_rate=CONFIG['risk_free_rate'])
            raw_allocations = ef.clean_weights()
            
            return {t: round(wt*100, 2) for t, wt in raw_allocations.items() if wt > 0.01}
        except Exception as e:
            print(f"Optimization Error: {str(e)}")
            return None

def main():
    analyzer = StockAnalyzer()
    
    # Step 1: Collect data with error handling
    print("Collecting stock data...")
    stocks_data = []
    for ticker in CONFIG['stock_universe']:
        try:
            data = analyzer.get_fundamentals(ticker)
            if data and not data['pe_ratio'] is None:
                data['rsi'] = analyzer.calculate_rsi(ticker)
                data['esg'] = analyzer.get_esg_score(ticker)
                print(f"Data for {ticker}: {data}")  # Debugging line
                stocks_data.append(data)
        except Exception as e:
            print(f"Main Error for {ticker}: {str(e)}")
    
    if not stocks_data:
        print("No valid data collected. Exiting.")
        return
    
    df = pd.DataFrame(stocks_data)
    
    # Step 2: Score stocks
    scored_df = analyzer.score_stocks(df)
    if scored_df.empty:
        print("No stocks passed scoring criteria.")
        return
    
    top_stocks = scored_df.head(6)  # Select top 6 for diversification
    
    # Step 3: Portfolio optimization
    print("\nOptimizing portfolio...")
    allocations = analyzer.optimize_portfolio(top_stocks)
    
    if not allocations:
        print("Portfolio optimization failed.")
        return
    
    # Display results
    print("\n=== Recommended Long-Term Portfolio ===")
    for ticker, allocation in allocations.items():
        stock_data = df[df['ticker'] == ticker].iloc[0]
        print(f"{ticker} ({stock_data['industry']})")
        print(f"  Allocation: {allocation}%")
        print(f"  Score: {stock_data['total_score']:.2f}")
        print(f"  P/E: {stock_data['pe_ratio']:.1f}  RSI: {stock_data['rsi']:.1f}")
        print(f"  ESG: {stock_data['esg']:.1f}\n")

if __name__ == "__main__":
    main()
