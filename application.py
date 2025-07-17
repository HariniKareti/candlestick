from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import datetime
import indicators

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Navbar
navbar = dbc.NavbarSimple(
    brand="📈 Indian Stock Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Stocks", href="/stocks")),
    ]
)

# Home page layout
home_layout = html.Div([
    html.H2("Welcome to Indian Stock Dashboard", className="mt-4"),
    html.P("Analyse Indian stocks with multiple technical indicators easily.")
], style={'padding': '20px'})

# Stocks page layout
stocks_layout = html.Div([
    html.Div(id='sticky-inputs', children=[
        dbc.Row([
            dbc.Col([
                html.P('Select Symbol:'),
                dcc.Dropdown(
                    id='symbol-dropdown',
                    options=[{'label': name, 'value': f"{name}.NS"} for name in ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN']],
                    value='RELIANCE.NS'
                )
            ], width=2),

            dbc.Col([
                html.P('Date Range (DD-MM-YYYY):'),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=datetime.date(2000, 1, 1),
                    max_date_allowed=datetime.date.today(),
                    display_format='DD-MM-YYYY',
                    start_date=datetime.date.today() - datetime.timedelta(days=180),
                    end_date=datetime.date.today()
                )
            ], width=3),

            dbc.Col([
                html.P("Indicators:"),
                dcc.Dropdown(
                    id='indicator-dropdown',
                    options=[
                        {'label': 'Simple Moving Average (SMA)', 'value': 'SMA'},
                        {'label': 'Exponential Moving Average (EMA)', 'value': 'EMA'},
                        {'label': 'Bollinger Bands', 'value': 'BB'},
                        {'label': 'Relative Strength Index (RSI)', 'value': 'RSI'},
                        {'label': 'MACD', 'value': 'MACD'},
                        {'label': 'Stochastic Oscillator', 'value': 'STOCH'},
                        {'label': 'Fibonacci Retracement', 'value': 'FIB'},
                        {'label': 'Ichimoku Cloud', 'value': 'ICHI'},
                        {'label': 'Standard Deviation', 'value': 'STD'},
                        {'label': 'Average Directional Index (ADX)', 'value': 'ADX'}
                    ],
                    multi=True,
                    placeholder="Select indicators to overlay"
                )
            ], width=4),

            dbc.Col([
                dbc.Button("Show Chart", id="submit-button", color="primary", className="mt-4")
            ], width=1)
        ], className='sticky-top bg-light p-2')
    ]),

    html.Div(id='chart-container', style={'marginTop': '20px'})
], style={'padding': '20px'})

# App layout with page routing
app.layout = html.Div([
    dcc.Location(id='url'),
    navbar,
    html.Div(id='page-content')
])

# Update page content based on URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/stocks':
        return stocks_layout
    else:
        return home_layout

# Callback to update chart
@app.callback(
    Output('chart-container', 'children'),
    Input('submit-button', 'n_clicks'),
    State('symbol-dropdown', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('indicator-dropdown', 'value')
)
def update_chart(n_clicks, symbol, start_date, end_date, indicators_selected):
    if n_clicks is None:
        return []

    if not (start_date and end_date):
        return html.Div("Please select a valid date range.")

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    data = yf.Ticker(symbol).history(start=start_date, end=end_date)
    if data.empty:
        return html.Div(f"No data for {symbol} between {start_date.strftime('%d-%m-%Y')} and {end_date.strftime('%d-%m-%Y')}.")

    data.reset_index(inplace=True)

    # Calculate y-axis range with padding for visible wicks
    price_min = data['Low'].min()
    price_max = data['High'].max()
    range_padding = (price_max - price_min) * 0.05

    # Create subplots
    rows = 1
    specs = [[{"secondary_y": False}]]
    subplot_titles = ['Candlestick Chart']

    for indicator in indicators_selected or []:
        if indicator in ['RSI', 'MACD', 'STOCH', 'ADX']:
            rows += 1
            specs.append([{"secondary_y": False}])
            subplot_titles.append(indicator)

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=subplot_titles)

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data['Date'], open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'], name='Candlestick'
    ), row=1, col=1)

    # SMA
    if 'SMA' in indicators_selected:
        data['SMA20'] = indicators.sma(data, 20)
        valid_sma = data[['Date', 'SMA20']].dropna()
        fig.add_trace(go.Scatter(
            x=valid_sma['Date'], y=valid_sma['SMA20'], mode='lines', name='SMA20', line=dict(color='blue')
        ), row=1, col=1)

    # EMA
    if 'EMA' in indicators_selected:
        data['EMA20'] = indicators.ema(data, 20)
        valid_ema = data[['Date', 'EMA20']].dropna()
        fig.add_trace(go.Scatter(
            x=valid_ema['Date'], y=valid_ema['EMA20'], mode='lines', name='EMA20', line=dict(color='orange')
        ), row=1, col=1)

    # Bollinger Bands
    if 'BB' in indicators_selected:
        bb_mid, bb_upper, bb_lower = indicators.bollinger_bands(data, 20)
        fig.add_trace(go.Scatter(x=data['Date'], y=bb_upper, mode='lines', name='BB Upper',
                                 line=dict(color='gray', dash='dot')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data['Date'], y=bb_lower, mode='lines', name='BB Lower',
                                 line=dict(color='gray', dash='dot')), row=1, col=1)

    # Indicators in subplots
    current_row = 2

    if 'RSI' in indicators_selected:
        data['RSI'] = indicators.rsi(data, 14)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['RSI'], mode='lines', name='RSI',
                                 line=dict(color='purple')), row=current_row, col=1)
        fig.update_yaxes(title_text="RSI Value", row=current_row, col=1)
        current_row += 1

    if 'MACD' in indicators_selected:
        macd_line, signal_line, histogram = indicators.macd(data)
        fig.add_trace(go.Scatter(x=data['Date'], y=macd_line, mode='lines', name='MACD Line',
                                 line=dict(color='black')), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=data['Date'], y=signal_line, mode='lines', name='Signal Line',
                                 line=dict(color='red')), row=current_row, col=1)
        fig.add_trace(go.Bar(x=data['Date'], y=histogram, name='MACD Histogram',
                             marker_color='green'), row=current_row, col=1)
        fig.update_yaxes(title_text="MACD", row=current_row, col=1)
        current_row += 1

    # Y-axis range update with padding for candlestick chart
    fig.update_yaxes(range=[price_min - range_padding, price_max + range_padding], row=1, col=1)

    # Final layout update
    fig.update_layout(height=300 * rows, showlegend=True,
                      title_text=f"{symbol} Technical Analysis ({start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')})",
                      xaxis_title="Date",
                      yaxis_fixedrange=False)

    return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
