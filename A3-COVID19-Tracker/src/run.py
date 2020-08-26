from app import app
from dash.dependencies import Input, Output
from layout.layout import build_desktop_layout
from pages.desktop import desktop_body
import dash_html_components as html
import dash_bootstrap_components as dbc



if __name__ == '__main__':
    app.layout = build_desktop_layout
    print('Currently running')
    app.run_server(port=5000)