from dash.exceptions import PreventUpdate
from scraper import initialize
from dash.dependencies import Input, Output, State


def register_callbacks(dashapp):
    @dashapp.callback(
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
