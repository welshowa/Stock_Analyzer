# main.py
import streamlit as st
from Scripts.Portfolio_logic import display_portfolio_view
import sqlite3
import pandas as pd


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Portfolio"])

if page == "Portfolio":
    display_portfolio_view()


# --- Connect to SQLite Database ---
def get_stock_data():
    conn = sqlite3.connect(r'C:\Users\elaho\Documents\StockScreener_PortfolioAnalyzer\DataBase\stocks.db')
    df = pd.read_sql("SELECT * FROM stocks", conn)
    conn.close()
    return df

# --- Portfolio logic ---
def calculate_portfolio_value(portfolio):
    df = get_stock_data()
    
    total_value = 0
    portfolio_returns = {}
    
    # Loop through each stock in the portfolio
    for stock, info in portfolio.items():
        stock_data = df[df['ticker'] == stock].iloc[0]  # Get stock data from DataFrame
        current_price = stock_data['price']
        
        # Calculate total value of each stock in the portfolio
        stock_value = current_price * info['quantity']
        total_value += stock_value
        
        # Calculate return on each stock in the portfolio
        stock_return = (current_price - info['purchase_price']) / info['purchase_price'] * 100
        portfolio_returns[stock] = stock_return
    
    return total_value, portfolio_returns
