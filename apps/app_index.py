import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

index_page = html.Div([
    html.Br(),
    dcc.Link('Go to Page age', href='/page-age'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
])