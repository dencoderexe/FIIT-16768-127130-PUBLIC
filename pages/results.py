from dash import html, dcc, Input, Output, callback

import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path_template="/results/<job_id>")

def layout(job_id=None, **kwargs):
    return dmc.Container(
        [
            dmc.Title(f"Results for job {job_id}", order=2),
            html.Div(id="result-page-content"),
            dcc.Store(id="result-job-id", data=job_id),
        ],
        fluid=True,
        p="md",
    )