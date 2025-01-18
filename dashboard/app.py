import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import redis
import json
from collections import deque

from dash import Dash, dcc, callback, Output, Input, State
from flask_cors import CORS
from datetime import datetime

app = Dash()

CORS(app.server)


def get_data_from_redis():
    r = redis.Redis(host='192.168.121.187', port=6379)
    json_metrics = json.loads(r.get('yuripereira-proj3-output').decode())
    return pd.DataFrame([json_metrics])


def get_new_df(redis_df, last_figure):
    if last_figure is None:
        redis_df['timestamp'] = pd.to_datetime(redis_df['timestamp']).dt.strftime('%H:%M:%S')
        df = redis_df
    else:
        dict_append = {}
        x = last_figure['data'][0]['x']
        x.append(datetime.strptime(redis_df['timestamp'][0], "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S"))
        len_to_remove = 0
        if len(set(x)) == 101:
            x = deque(x)
            value = x.popleft()
            len_to_remove = x.count(value)
            x = [x for x in x if x != value]
        
        for data in last_figure['data']:
            y = data['y']
            y.append(redis_df[data['name']][0])
            if len_to_remove != 0:
                y = y[len_to_remove:]
            
            dict_append[data['name']] = y
        
        dict_append['timestamp'] = x
        df = pd.DataFrame.from_dict(dict_append, orient='index').transpose()
    
    df_long = df.melt(id_vars="timestamp", var_name="variable", value_name="value")
    return df_long


app.layout = dmc.Container(
    [
        dmc.Title('Resource usage analysis', color="black", size="h2", align="center"),
        dmc.Grid(
            [
                dmc.Col([dcc.Graph(id='network-egress')], span=6),
                dmc.Col([dcc.Graph(id='memory-caching')], span=6),
            ]
        ),
        dmc.Grid([dmc.Col([dcc.Graph(id='avg-util-cpu')], span=12)]),
        dcc.Interval(id='interval-component'),
    ],
    fluid=True,
)


@callback(
    Output('network-egress', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('network-egress', 'figure'),
)
def update_metrics(n, last_figure):
    redis_df = get_data_from_redis()
    redis_df = redis_df[['percent-network-egress', 'timestamp']]
    new_df = get_new_df(redis_df, last_figure)
    
    fig = px.line(new_df, x="timestamp", y="value", color="variable", title="Line Plot")
    return fig


@callback(
    Output('memory-caching', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('memory-caching', 'figure'),
)
def update_metrics(n, last_figure):
    redis_df = get_data_from_redis()
    redis_df = redis_df[['percent-memory-caching', 'timestamp']]
    new_df = get_new_df(redis_df, last_figure)

    fig = px.line(new_df, x="timestamp", y="value", color="variable", title="Line Plot")
    return fig


@callback(
    Output('avg-util-cpu', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('avg-util-cpu', 'figure'),
)
def update_metrics(n, last_figure):
    redis_df = get_data_from_redis()
    del redis_df['percent-memory-caching']
    del redis_df['percent-network-egress']
    new_df = get_new_df(redis_df, last_figure)

    fig = px.line(new_df, x="timestamp", y="value", color="variable", title="Line Plot")
    return fig


if __name__ == '__main__':
    app.run(debug=True, port="52064", host="0.0.0.0")
