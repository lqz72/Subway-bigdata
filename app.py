import dash

external_stylesheets = ['D:/python/code/static/common.css']

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
server = app.server