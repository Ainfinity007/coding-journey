from dash import Dash, html, dcc
import plotly.express as px
import sqlite3

app = Dash(__name__)

def update_layout():
    conn = sqlite3.connect('../data/solutions.db')
    df = pd.read_sql('SELECT * FROM problems', conn)
    
    return html.Div([
        html.H1("Coding Progress"),
        dcc.Graph(figure=px.pie(df, names='difficulty')),
        dcc.Graph(figure=px.bar(df, x='tags')),
        dcc.Interval(id='interval', interval=30000)
    ])

if __name__ == '__main__':
    app.run_server(port=8050)
