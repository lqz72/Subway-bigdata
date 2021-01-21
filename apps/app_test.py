import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

page_2_layout = html.Div([
    html.H1('Page 2'),

    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Page age', href='/page-age'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])