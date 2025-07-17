# app.py

# 📌 Imports
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import datetime

# 📌 Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 📌 Indian stock symbols with .NS suffix for NSE
INDIAN_SYMBOLS = {
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'INFY': 'INFY.NS',
    'HDFCBANK': 'HDFCBANK.NS',
    'ICICIBANK': 'ICICIBANK.NS',
    'SBIN': 'SBIN.NS'
}

# 📌 Layout components

symbol_dropdown = html.Div([
    html.P('Select Symbol:'),
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': name, 'value': symbol} for name, symbol in INDIAN_SYMBOLS.items()],
        value='RELIANCE.NS'
    )
])

num_days_input = html.Div([
    html.P('Number of Past Days:'),
    dbc.Input(id='num-days-input', type='number', value=30, min=1, max=365)
])

submit_button = dbc.Button("Show Chart", id="submit-button", color="primary", className="mt-2")

# 📌 App layout
app.layout = html.Div([
    html.H1('📈 Indian Stock Market Dashboard'),

    dbc.Row([
        dbc.Col(symbol_dropdown),
        dbc.Col(num_days_input),
        dbc.Col(submit_button)
    ]),

    html.Hr(),

    html.Div(id='chart-container')
], style={'margin': '20px'})

# 📌 Callback to update candlestick chart
@app.callback(
    Output('chart-container', 'children'),
    Input('submit-button', 'n_clicks'),
    State('symbol-dropdown', 'value'),
    State('num-days-input', 'value')
)
def update_chart(n_clicks, symbol, num_days):
    if n_clicks is None:
        return []

    end_date = datetime.datetime(2024, 7, 17)
    start_date = end_date - datetime.timedelta(days=int(num_days))

    # Fetch data using Ticker().history() instead of download()
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date)

    if data.empty:
        return html.Div(f"No data found for {symbol} between {start_date.date()} and {end_date.date()}.")

    data.reset_index(inplace=True)

    # Plotly candlestick chart
    fig = go.Figure(data=go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    ))

    fig.update_layout(
        title=f"{symbol} Candlestick Chart ({start_date.date()} to {end_date.date()})",
        yaxis_title='Price (INR)',
        xaxis_title='Date',
        xaxis_rangeslider_visible=False
    )

    return dcc.Graph(figure=fig)

# 📌 Run the app
if __name__ == '__main__':
    app.run(debug=True)
