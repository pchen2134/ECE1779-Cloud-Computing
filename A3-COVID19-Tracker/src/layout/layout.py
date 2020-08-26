import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from pages.desktop import desktop_body

build_desktop_layout = html.Div(
    [  
        dbc.Container(desktop_body, id="dash-content", className="dash-container", fluid=True),
    ],
    style={"padding": "2%", "color": "#003300", "margin-bottom": "20px", "overflow-y": "scroll"}
)