import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sys
sys.path.append("../..")
from data import age

colors = {
    'background': '#DCDCDC',
    'text': '#7FDBFF'
}

file_path = "D:/python/code/data/users.csv"

age_data = age.Age_Structure(file_path)
age_struct = age_data.get_structure()
age_dict = age_data.process_data()

df = pd.DataFrame({
    "年龄段": age_struct[0],
    "占比/%": age_struct[1],
})

df_all = pd.DataFrame({
    "年龄 /岁": list(age_dict.keys()),
    "人数": list(age_dict.values())
})

fig = px.bar(df, x="年龄段", y="占比/%", color="年龄段")
fig_pie = px.pie(df, values='占比/%', names='年龄段', color="年龄段")
fig_bar = px.bar(df_all, x = "年龄 /岁", y = "人数")

page_age_layout = html.Div([
    html.H1(
        children= '用户年龄结构分析',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Welcome to our website!', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Tabs([
        dcc.Tab(label="各年龄段人数的分布",children=[
            dcc.Graph(
                id='graph-1',
                figure=fig
            )
        ]),

        dcc.Tab(label="各年龄人数的分布",children=[
            dcc.Graph(
                id='graph-3',
                figure=fig_bar
            )
        ]),
        dcc.Tab(label="用户年龄结构图",children=[
            dcc.Graph(
                id='graph-2',
                figure=fig_pie
            )
        ])
    ], vertical=True),

    html.Div(id='page-age-content'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
])



