import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import app_index, app_age, app_sta_flow, app_404

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Update the index
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/age':
        return app_age.page_age_layout
    elif pathname == '/station-flow':
        return app_sta_flow.page_sta_flow_layout
    elif pathname == "/":
        return app_index.index_page
    else:
        return app_404.page_404_layout

if __name__ == '__main__':
    app.run_server(debug=True)