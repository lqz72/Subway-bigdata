import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

colors = {
    'background': '#DCDCDC',
    'text': '#506784'
}

index_page = html.Div(
    children = [
    html.Div([
        dcc.Link('Go to Page age', href='/age', style= {'color':colors['text']}),
        html.Br(),
        dcc.Link('Go to Page station-flow', href='/station-flow', style= {'color':colors['text']}),
        html.Hr(),
    ])
])