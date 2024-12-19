import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State

from api import get_weather
from exceptions import APIError

app = Dash(__name__)
app.layout = html.Div([
    html.H1('Погода'),
    html.Div(id='inputs', children=[]),
    html.Button('Получить погоду', id='get_weather_button', n_clicks=0),
    html.Button('Добавить город', id='add_city_button', n_clicks=0),
    dcc.Graph(id='graphic'),
    html.Div(id='error', style={'color': 'red'})
])
colors = px.colors.qualitative.Plotly


@app.callback(
    Output('inputs', 'children'),
    Input('add_city_button', 'n_clicks'),
    State('inputs', 'children'),
)
def add_city_input(n_clicks, children):
    children.append(dcc.Input(
        id=f'city{n_clicks}',
        type='text',
        placeholder='Введите город',
    ))
    return children


@app.callback(
    Output('graphic', 'figure'),
    Output('error', 'children'),
    Input('get_weather_button', 'n_clicks'),
    Input('inputs', 'children'),
)
def update_graph(n_clicks, city_inputs):
    if n_clicks > 0:
        dfs = []
        errors = []
        names = []
        for input_component in city_inputs:
            try:
                names.append(input_component['props']['value'])
            except (ValueError, IndexError):
                errors.append(f'Город не введен')

        for name in names:
            try:
                weather = get_weather(name)
                dfs.append(pd.DataFrame(weather))
            except APIError as err:
                errors.append(f'Ошибка для города {name}: {err.message}')
                continue

        fig = go.Figure()

        for i in range(len(dfs)):
            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=dfs[i]['date'],
                y=dfs[i]['temperature'],
                mode='lines+markers',
                name=f'Средняя температура в {names[i]}',
                line={'color': color},
            ))

        fig.update_layout(title='Прогноз погоды на 5 дней',
                          xaxis_title='Дата',
                          yaxis_title='Температура (°C)',
                          legend_title='Города')

        return fig, 'Ошибочки: ' + ', '.join(errors)
    else:
        return go.Figure(), ''


if __name__ == '__main__':
    app.run_server('127.0.0.1', 8080)
