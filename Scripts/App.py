from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import yfinance as yf
import dash

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Function to fetch stock data from Yahoo Finance
def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)  # Fetch stock data
    df = stock.history(period=period)  # Fetch historical data
    return df, stock  # Return both the dataframe and the stock object

# Define the layout of the app
app.layout = html.Div(
    children=[
        dbc.Container(
            children=[
                html.H1("Stock Analyzer & Screener", className="text-center my-4"),

                # Stock Search Bar
                dbc.Row(
                    [
                        dbc.Col(dbc.Input(id='stock-input', placeholder="Enter stock ticker", type="text"), width=8),
                        dbc.Col(dbc.Button("Search", id='search-button', color="primary"), width=4),
                    ],
                    className="mb-4"
                ),

                # Dropdown for time period selection
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id='time-period',
                                options=[
                                    {'label': '1 Day', 'value': '1d'},
                                    {'label': '1 Week', 'value': '1wk'},
                                    {'label': '1 Month', 'value': '1mo'},
                                    {'label': '3 Months', 'value': '3mo'},
                                    {'label': '1 Year', 'value': '1y'},
                                    {'label': '5 Years', 'value': '5y'},
                                    {'label': 'Max', 'value': 'max'},
                                ],
                                value='1y',  # Default value
                                className="mb-4"
                            ),
                            width=4
                        ),
                    ]
                ),

                # Indicator for price change (up or down)
                html.Div(id='price-indicator', className="text-center my-2"),

                # Graph display for stock chart
                dcc.Graph(id='stock-graph', config={'displayModeBar': 'hover'}),

                # Display stock info under the graph
                html.Div(id='stock-info', className="my-4")
            ]
        )
    ]
)

# Callback to update the stock chart based on the ticker input and time period
@app.callback(
    [dash.dependencies.Output('stock-graph', 'figure'),
     dash.dependencies.Output('stock-info', 'children'),
     dash.dependencies.Output('price-indicator', 'children')],
    [dash.dependencies.Input('search-button', 'n_clicks')],
    [dash.dependencies.State('stock-input', 'value'),
     dash.dependencies.State('time-period', 'value')]
)
def update_graph(n_clicks, stock_ticker, time_period):
    if n_clicks is None or not stock_ticker:
        return {}, "Enter a valid stock ticker to see data.", ""
    
    # Fetch the stock data and the stock object
    try:
        df, stock = get_stock_data(stock_ticker, period=time_period)

        # Determine if the price is up or down and calculate price and percentage change
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        price_change = end_price - start_price
        percent_change = (price_change / start_price) * 100
        
        # Create the indicator text and color
        if price_change > 0:
            price_indicator = html.H4(
                f"Price is up by {price_change:.2f} USD ({percent_change:.2f}%)",
                style={'color': 'green'}
            )
        else:
            price_indicator = html.H4(
                f"Price is down by {abs(price_change):.2f} USD ({abs(percent_change):.2f}%)",
                style={'color': 'red'}
            )
        
        # Create a plotly figure with the stock data
        fig = go.Figure()

        # Add line trace for stock closing price with custom color (green for price up, red for down)
        line_color = 'green' if price_change > 0 else 'red'
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color=line_color)))
        
        # Customize the layout
        fig.update_layout(
            title=f"{stock_ticker} - Stock Price",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template='plotly_white',  # White background
            hovermode="closest",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        # Display basic stock info
        stock_info = [
            dbc.Row([
                dbc.Col(html.P(f"{stock.info.get('longName', 'Company Name Unavailable')}"), width=4),
                dbc.Col(html.P(f"Latest Close: {df['Close'].iloc[-1]:.2f} USD"), width=4),
                dbc.Col(html.P(f"Market Cap: {stock.info.get('marketCap', 'N/A'):,} USD"), width=4),
            ]),
            dbc.Row([
                dbc.Col(html.P(f"Earnings Date: {stock.info.get('nextEarningsDate', 'N/A')}"), width=4),
                dbc.Col(html.P(f"Beta: {stock.info.get('beta', 'N/A')}"), width=4),
                dbc.Col(html.P(f"Dividend Yield: {stock.info.get('dividendYield', 'N/A') * 100 if 'dividendYield' in stock.info else 'N/A'}%"), width=4),
            ]),
            dbc.Row([
                dbc.Col(html.P(f"Average Volume: {stock.info.get('averageVolume', 'N/A')}"), width=4),
                dbc.Col(html.P(f"Shares Outstanding: {stock.info.get('sharesOutstanding', 'N/A')}"), width=4),
                dbc.Col(html.P(f"Revenue (TTM): {stock.info.get('totalRevenue', 'N/A'):,} USD"), width=4),
            ]),
            dbc.Row([
                dbc.Col(html.P(f"Gross Profit: {stock.info.get('grossProfits', 'N/A'):,} USD"), width=4),
                dbc.Col(html.P(f"Return on Equity: {stock.info.get('returnOnEquity', 'N/A')}%"), width=4),
                dbc.Col(html.P(f"Debt to Equity: {stock.info.get('debtToEquity', 'N/A')}"), width=4),
            ]),
            dbc.Row([
                dbc.Col(html.P(f"Volume: {stock.info.get('volume', 'N/A')}"), width=4),
                dbc.Col(html.P(f"Institutional Ownership: {stock.info.get('institutionOwnership', 'N/A')}%"), width=4),
                dbc.Col(html.P(f"Insider Ownership: {stock.info.get('insiderOwnership', 'N/A')}%"), width=4),
            ])
        ]
        
        return fig, stock_info, price_indicator
    
    except Exception as e:
        return {}, [html.P(f"Error fetching data for {stock_ticker}: {str(e)}")], ""

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
