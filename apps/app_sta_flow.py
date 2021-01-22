import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data import station_flow
from app import app

colors = {
    'background': '#DCDCDC',
    'text': '#7FDBFF'
}

#获取数据
sta_file_path = './data/station.csv'
trips_file_path = './data/trips.csv'
sta_flow = station_flow.Station_Flow(sta_file_path, trips_file_path)
in_data, out_data = sta_flow.process_data()
sta_list = list(in_data.keys())

page_sta_flow_layout = html.Div([
    html.H1(
        children= '单站的点出/入站客流分析',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div([
        html.P('站点: '),
        dcc.Dropdown(
            id='drop_down',
            options=[{'label': i, 'value': i} for i in sta_list],
            value= sta_list[0]
        ),
        html.P('类型'),
        dcc.RadioItems(
            id='radio_items',
            options=[{'label': i, 'value': i} for i in ['出站', '入站', '出/入站']],
            value= '出站',
            labelStyle={'display': 'inline-block'}
        )
    ],
    style={'width': '40%', 'display': 'inline-block'}
    ),

    html.Br(),

    html.Div([dcc.Graph(id='graph')], style = {'width': '80%', 'display': 'inline-block'}),

    html.Div(id='station-flow'),
    html.Br(),
    dcc.Link('Go to Page age', href='/age'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])

@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('drop_down', 'value'),
     dash.dependencies.Input('radio_items', 'value'),])
def update_graph(station_name, display_type):

    in_sta_data = in_data[station_name]
    out_sta_data = out_data[station_name]

    df_in = pd.DataFrame({
        '日期': list(in_sta_data.keys()),
        '客流量 /人次': list(in_sta_data.values())
    })

    df_out = pd.DataFrame({
        '日期': list(out_sta_data.keys()),
        '客流量 /人次': list(out_sta_data.values())
    })

    date_list = list(out_sta_data.keys()) + list(in_sta_data.keys())
    amount_list = list(out_sta_data.values()) + list(in_sta_data.values())
    in_num = len(list(out_sta_data.keys()))
    out_num = len(list(in_sta_data.keys()))
    type_list = ['出站' for i in range(out_num)] + ['入站' for i in range(in_num)]

    df_all = pd.DataFrame({
        '日期': date_list,
        '客流量 /人次': amount_list,
        '类型': type_list
    })

    if display_type == '入站':
        fig = px.bar(df_in, x= '日期', y= '客流量 /人次', color='日期')
    elif display_type == '出站':
        fig = px.bar(df_out, x='日期', y='客流量 /人次', color='日期')
    else:
        fig = px.bar(df_all, x='日期', y='客流量 /人次', color= '类型', barmode="group")
    return fig