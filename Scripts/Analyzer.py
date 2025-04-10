# Analyzer.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Define the layout for the stock analyzer
layout = html.Div(
    children=[
        dbc.Container(
            children=[
                html.H1("Stock Analyzer", className="text-center my-4"),

                # Stock Search Bar
                dbc.Row(
                    [
                        dbc.Col(dbc.Input(id='stock-input-analyzer', placeholder="Enter stock ticker", type="text"), width=8),
                        dbc.Col(dbc.Button("Search", id='search-button-analyzer', color="primary"), width=4),  # Removed block=True
                    ],
                    className="mb-4"
                ),

                # Graph display for stock chart
                dcc.Graph(id='stock-graph-analyzer', config={'displayModeBar': 'hover'}),

                # Display stock info under the graph
                html.Div(id='stock-info-analyzer', className="my-4")
            ]
        )
    ]
)
