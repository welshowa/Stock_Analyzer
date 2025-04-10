# Screening.py
import sqlite3
import pandas as pd
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# Load data from SQLite
conn = sqlite3.connect(r'C:\Users\elaho\Documents\StockScreener_PortfolioAnalyzer\DataBase\stocks.db')
df = pd.read_sql("SELECT * FROM stocks", conn)
conn.close()

# Clean data: Drop rows with NaN values in relevant columns
df = df.dropna(subset=['sector', 'pe_ratio', 'dividend_yield', 'market_cap'])

# Generate sector options
sector_options = [{'label': sec, 'value': sec} for sec in sorted(df['sector'].unique())]
sector_options.insert(0, {'label': 'All Sectors', 'value': 'All'})

# Define layout
layout = html.Div([  # Expose 'layout' for import
    html.H2("Stock Screener"),
    dbc.Row([ 
        dbc.Col([ 
            html.Label("Sector"),
            dcc.Dropdown(id='sector-filter', options=sector_options, value='All'),

            html.Label("Min P/E Ratio"),
            dcc.Input(id='min-pe', type='number', value=1),

            html.Label("Max P/E Ratio"),
            dcc.Input(id='max-pe', type='number', value=100),

            html.Label("Min Dividend Yield (%)"),
            dcc.Input(id='min-div', type='number', value=0.5, step=0.1),

            html.Label("Min Market Cap ($B)"),
            dcc.Input(id='min-mcap', type='number', value=10),

            html.Br(),
            html.Br(),
            dbc.Button("Apply Filters", id='filter-button', color='primary')
        ], width=3),

        dbc.Col([ 
            html.H4("Matching Stocks"),
            html.Div(id='screener-output')
        ], width=9)
    ])
])

# Callback to filter stocks based on inputs
def filter_stocks(n_clicks, sector, min_pe, max_pe, min_div, min_mcap):
    # Avoid running filter before clicking the button
    if n_clicks is None:
        return html.P("Please apply filters to see matching stocks.")

    # Ensure valid numerical input
    try:
        min_pe = float(min_pe)
        max_pe = float(max_pe)
        min_div = float(min_div)
        min_mcap = float(min_mcap)
    except ValueError:
        return html.P("Please enter valid numbers for all filters.")

    # Apply filters
    filtered = df[
        (df['pe_ratio'] >= min_pe) &
        (df['pe_ratio'] <= max_pe) &
        (df['dividend_yield'] >= min_div / 100) &
        (df['market_cap'] >= min_mcap * 1e9)
    ]

    if sector != 'All':
        filtered = filtered[filtered['sector'] == sector]

    if filtered.empty:
        return html.P("No stocks match your criteria.")

    return dbc.Table.from_dataframe(
        filtered[['ticker', 'company', 'sector', 'pe_ratio', 'dividend_yield', 'market_cap', 'price']],
        striped=True, bordered=True, hover=True
    )
