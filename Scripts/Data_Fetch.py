import yfinance as yf
import pandas as pd
import sqlite3
import os
import streamlit as st

# --- Setup ---
Symbols = [
    'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'JPM', 'META',  
    'NFLX', 'NVDA', 'INTC', 'V', 'BA', 'DIS', 'IBM', 'PYPL',
    'WMT', 'KO', 'GS', 'CRM', 'AMD', 'PFE', 'UNH', 'LNR.TO'
]

# Create directories if they don't exist
os.makedirs('DataBase', exist_ok=True)
os.makedirs('data', exist_ok=True)

# --- Connect to SQLite ---
conn = sqlite3.connect('DataBase/stocks.db')
cursor = conn.cursor()

# --- Create Table ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS stocks (
    ticker TEXT PRIMARY KEY,
    company TEXT,
    sector TEXT,
    pe_ratio REAL,
    market_cap REAL,
    dividend_yield REAL,
    price REAL
);
""")

# --- Fetch + Store Data ---
data = []

# Default values for missing data
default_values = {
    'pe_ratio': 0.0,
    'market_cap': 0.0,
    'dividend_yield': 0.0,
    'price': 0.0
}

for S in Symbols:
    try:
        stock_info = yf.Ticker(S).info

        stock_data = {
            'Symbol': S,
            'company': stock_info.get('shortName', 'N/A'),
            'sector': stock_info.get('sector', 'N/A'),
            'pe_ratio': stock_info.get('trailingPE', default_values['pe_ratio']),
            'market_cap': stock_info.get('marketCap', default_values['market_cap']),
            'dividend_yield': stock_info.get('dividendYield', default_values['dividend_yield']),
            'price': stock_info.get('currentPrice', default_values['price'])
        }

        data.append(stock_data)

        cursor.execute("""
        INSERT OR REPLACE INTO stocks VALUES (?, ?, ?, ?, ?, ?, ?)
        """, tuple(stock_data.values()))

    except Exception as e:
        print(f"Error fetching {S}: {e}")

conn.commit()
df = pd.DataFrame(data)
df.to_csv('data/raw_data.csv', index=False)
print("Data fetching complete and committed to SQLite.")
conn.close()
print("Data saved to CSV as backup.")

# --- Streamlit Component: Stock Details ---
def display_stock_details():
    st.title("📊 Stock Details Viewer")
    
    # Reload data from SQLite
    conn = sqlite3.connect('DataBase/stocks.db')
    df = pd.read_sql_query("SELECT * FROM stocks", conn)
    conn.close()

    ticker = st.selectbox("Choose a stock ticker:", df['ticker'].sort_values())
    stock = df[df['ticker'] == ticker].iloc[0]

    st.subheader(f"Details for {ticker} - {stock['company']}")
    st.write("**Sector:**", stock['sector'])
    st.write("**Price:** $", round(stock['price'], 2))
    st.write("**P/E Ratio:**", stock['pe_ratio'])
    st.write("**Market Cap:**", f"{stock['market_cap']:,}")
    st.write("**Dividend Yield:**", stock['dividend_yield'])
