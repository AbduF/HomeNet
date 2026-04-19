from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__, requests_pathname_prefix='/dashboard/')

app.layout = html.Div([
    html.H1("HomeNet Admin Dashboard"),
    dcc.Graph(id='traffic-graph'),
    dcc.Interval(id='interval', n_intervals=0, interval=1000)
])

@app.callback(Output('traffic-graph', 'figure'),
              Input('interval', 'n_intervals'))
def update_traffic(n):
    # Simulate traffic data (replace with real Scapy/psutil data)
    df = pd.DataFrame({
        'time': pd.date_range(start='2026-01-01', periods=10, freq='1min'),
        'traffic': [10, 20, 15, 25, 30, 20, 10, 5, 15, 25]
    })
    fig = px.line(df, x='time', y='traffic', title='Network Traffic')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)