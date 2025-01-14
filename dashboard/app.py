import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import redis
import json

from dash import Dash, dcc, callback, Output, Input, State
from flask_cors import CORS

app = Dash()

CORS(app.server)


def get_data_from_redis():
    r = redis.Redis(host='192.168.121.187', port=6379)
    json_metrics = json.loads(r.get('yuripereira-proj3-output').decode())
    return pd.DataFrame([json_metrics])


def get_new_df(redis_df, last_figure):
    if last_figure is None:
        return redis_df
    else:
        dict_append = {}
        for data in last_figure['data']:
            y = data['y']
            y.append(redis_df[data['name']][0])
            dict_append[data['name']] = y

    return pd.DataFrame.from_dict(dict_append, orient='index').transpose()


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
        dcc.Interval(id='interval-component', interval=2000),
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
    redis_df = redis_df[['percent-network-egress']]
    new_df = get_new_df(redis_df, last_figure)

    fig = px.line(new_df)
    return fig


@callback(
    Output('memory-caching', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('memory-caching', 'figure'),
)
def update_metrics(n, last_figure):
    redis_df = get_data_from_redis()
    redis_df = redis_df[['percent-memory-caching']]
    new_df = get_new_df(redis_df, last_figure)

    fig = px.line(new_df)
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

    fig = px.line(new_df)
    return fig


if __name__ == '__main__':
    app.run(debug=True, port="52064", host="0.0.0.0")
