import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import dash_table

# Carga tus datos
importaciones = pd.read_excel(
    './data2/IMPORTACION-VOLUMEN-2023-05.xlsx', skiprows=6)
consumo = pd.read_excel('./data2/CONSUMO-2023-05.xlsx', skiprows=6)
precios_2023 = pd.read_excel(
    './data2/Precios-Promedio-Nacionales-Diarios-2023.xlsx', sheet_name=0, skiprows=7)
precios_2022 = pd.read_excel(
    './data2/Precios-Promedio-Nacionales-Diarios-2023.xlsx', sheet_name=1, skiprows=6)
precios_2021 = pd.read_excel(
    './data2/Precios-Promedio-Nacionales-Diarios-2023.xlsx', sheet_name=2, skiprows=6)

# Ruta donde se encuentran los archivos Excel exportados
ruta_exportacion = 'dataClean/'

# Importar datos de importaciones desde el archivo Excel
importas = pd.read_excel(f'{ruta_exportacion}importaciones.xlsx')

# Importar datos de consumo desde el archivo Excel
consumas = pd.read_excel(f'{ruta_exportacion}consumo.xlsx')

# Importar datos de precios desde el archivo Excel
preciosas = pd.read_excel(f'{ruta_exportacion}precios.xlsx')


# Colores personalizados para el control deslizante
custom_colors = ['#e63946', '#f1faee', '#a8dadc', '#457b9d', '#1d3557']


# Tipos de gráfico disponibles
chart_types = ['scatter', 'bar', 'line', 'histogram']

app = dash.Dash(__name__, external_stylesheets=[
                'https://codepen.io/chriddyp/pen/bWLwgP.css'])  # Usar CSS de Dash básico

app.layout = html.Div([
    # Título
    html.Div([html.H1("Visualizacion Interactiva")], style={
             'textAlign': 'center', 'marginBottom': '25px'}),

    # Contenedor principal
    html.Div([
        # Contenedor para los selectores
        html.Div([
            html.Label('Seleccione un conjunto de datos:'),
            dcc.Dropdown(
                id='data-selector',
                options=[
                    {'label': 'Importaciones', 'value': 'importaciones'},
                    {'label': 'Consumo', 'value': 'consumo'},
                    {'label': 'Precios', 'value': 'precios'}
                ],
                value='importaciones',
                clearable=False
            ),

            html.Label('Seleccione un tipo de gráfico:'),
            dcc.Dropdown(
                id='chart-type',
                options=[
                    {'label': 'Scatter', 'value': 'scatter'},
                    {'label': 'Bar', 'value': 'bar'},
                    {'label': 'Line', 'value': 'line'},
                    {'label': 'Histogram', 'value': 'histogram'}
                ],
                value='scatter',
                clearable=False
            ),

            html.Label('Seleccione un color para el gráfico:'),
            dcc.Slider(
                id='color-slider',
                min=0,
                max=len(custom_colors) - 1,
                step=1,
                value=0,
                marks={i: custom_colors[i] for i in range(len(custom_colors))}
            ),
        ], style={'width': '30%', 'float': 'left', 'marginRight': '3%'}),

        # Contenedor para el gráfico
        html.Div([
            dcc.Graph(id='data-graph'),
            html.Div(id='data-description',
                     style={'marginTop': '20px', 'fontSize': '18px', 'fontWeight': 'bold'})
        ], style={'width': '67%', 'float': 'left'})
    ], style={'display': 'flex', 'flexDirection': 'row'}),

    # Botón y tabla
    html.Div([
        html.Button('Mostrar/Ocultar Tabla', id='toggle-button',
                    style={'marginTop': '20px'}),
        html.Div(dash_table.DataTable(id='data-table', style_table={
                 'overflowX': 'scroll'}), id='table-container', style={'display': 'none'})
    ])
], style={'maxWidth': '1200px', 'margin': '0 auto'})

# Callback para mostrar/ocultar la tabla


@app.callback(
    Output('table-container', 'style'),
    Output('toggle-button', 'children'),
    [Input('toggle-button', 'n_clicks')],
    State('table-container', 'style')
)
def toggle_table(n_clicks, current_style):
    if n_clicks is None:
        return current_style, 'Mostrar Tabla'
    if current_style.get('display') == 'none':
        return {'display': 'block'}, 'Ocultar Tabla'
    return {'display': 'none'}, 'Mostrar Tabla'


# Callback para actualizar los gráficos, descripción y tabla de datos
@app.callback(
    [Output('data-graph', 'figure'), Output('data-description', 'children'),
     Output('data-table', 'columns'), Output('data-table', 'data')],
    [Input('data-selector', 'value'), Input('chart-type',
                                            'value'), Input('color-slider', 'value')]
)
def update_data(selected_data, chart_type, color_value):
    data = None
    description = ""
    table_columns = []
    table_data = []
    if selected_data == 'importaciones':
        data = importas
        description = "Datos de importaciones"
    elif selected_data == 'consumo':
        data = consumas
        description = "Datos de consumo"
    elif selected_data == 'precios':
        data = preciosas
        description = "Datos de precios"

    if data is not None:
        if chart_type == 'scatter':
            fig = px.scatter(data, x=data.columns[0], y=data.columns[1])

            # Escala de color en función de la posición relativa en el eje Y
            fig.update_traces(marker=dict(
                color=data.index, colorscale='Viridis'))
        elif chart_type == 'bar':
            fig = px.bar(data, x=data.columns[0], y=data.columns[1])
        elif chart_type == 'line':
            fig = px.line(data, x=data.columns[0], y=data.columns[1])
        elif chart_type == 'histogram':
            fig = px.histogram(data, x=data.columns[1])

        # Aplicar el color seleccionado del control deslizante
        selected_color = custom_colors[color_value]
        fig.update_traces(marker=dict(color=selected_color))

        # Configurar las columnas y datos para la tabla
        table_columns = [{'name': col, 'id': col} for col in data.columns]
        table_data = data.to_dict('records')

        return fig, description, table_columns, table_data
    else:
        return {}, "", [], []


if __name__ == '__main__':
    app.run_server(debug=True)
