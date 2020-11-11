import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from scraper import initialize

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


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


app.layout = serve_layout


@app.callback(
    [Output('jobs-table', 'columns'),
     Output('jobs-table', 'data')],
    [Input('submit-search', 'n_clicks')],
    [State('job-query', 'value'),
     State('job-loc-query', 'value'),
     State('pages-query', 'value')]
)
def search(n_clicks: int, job_value: str, loc_value: str, pages: int):
    if n_clicks is not None:
        if job_value is not None and loc_value is not None and pages is not None:
            jobs_df = initialize(job_value, loc_value, pages)
            columns = [{'name': i, "id": i} for i in
                       jobs_df[jobs_df.columns[~jobs_df.columns.isin(['job_description'])]]]
            data = jobs_df.to_dict('records')
            return columns, data
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
