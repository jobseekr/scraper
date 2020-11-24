import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html


def serve_layout():
    return html.Div(id='main', children=[
        html.Nav(children=[
            html.H1("Job Seeker v1.0"),
            html.I(children=['By ', html.A('Kanisk Chakraborty', href='https://github.com/chakrakan')])
        ]),
        html.Div(id='search-container', children=[
            html.Label('Job Title'),
            dcc.Input(id='job-query', type='text', placeholder="Job Title..."),
            html.Label('Location'),
            dcc.Input(id='job-loc-query', type='text', placeholder="Location"),
            html.Label('Pages'),
            dcc.Input(id='pages-query', type='number', placeholder=1, min=1, max=100, value=1),
            html.Br(), html.Br(),
            html.Button("Submit", id="submit-search", n_clicks=0),
            html.Br(), html.Br(),
            html.Div(id='res-container')
        ], style={'padding-top': '20px'}),
        html.Div(id='data-table-container', children=[
            dash_table.DataTable(id='jobs-table')
        ])
    ])


def init_dashboard(server):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashboard/',
        external_stylesheets=external_stylesheets
    )
    dash_app.layout = serve_layout
    return dash_app.server
