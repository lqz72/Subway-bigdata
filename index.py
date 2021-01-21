import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import app_index, app_age, app_test, app_404

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Update the index
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-age':
        return app_age.page_age_layout
    elif pathname == '/page-2':
        return app_test.page_2_layout
    elif pathname == "/":
        return app_index.index_page
    else:
        return app_404.page_404_layout

if __name__ == '__main__':
    app.run_server(debug=True)