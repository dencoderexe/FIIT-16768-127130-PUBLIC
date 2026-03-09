import dash
from dash import Input, Output, State, callback, dcc, html, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.job_signal import get_signal
from services.job_manager import get_jobs, Status, Tool, Job, Step#, create_job

dash.register_page(__name__, path="/jobs")

def make_status_icon(status: Status):
    return dmc.ThemeIcon(
        DashIconify(icon=status.icon, height=18),
        color=status.color,
        variant="light",
        radius="xl",
        size="md",
    )

def make_step_row(step: Step):
    return dmc.Group(
        children=[
            dmc.ThemeIcon(
                DashIconify(icon=step.status.icon, height=14),
                color=step.status.color,
                variant="light",
                radius="xl",
                size="sm",
            ),
            dmc.Text(step.name, size="sm"),
        ],
        gap="sm",
        align="center",
    )

def make_job_item(job: Job):
    """

    """
    header = dmc.Group(
        children=[
            dmc.Stack(
                [
                    dmc.Text(job.started_at.strftime("%d.%m.%Y %H:%M:%S"), size="xs", c="dimmed"),
                    dmc.Text(job.tool.tool_name, size="sm", fw=600),
                ],
                gap=2,
            ),
            make_status_icon(job.status),
        ],
        justify="space-between",
        align="center",
        w="100%",
    )

    body = dmc.Stack(
        children=[
            dmc.Text(job.tool.tool_description, size="sm", c="dimmed"),
            dmc.Divider(),
            dmc.Stack(
                [make_step_row(step) for step in job.steps],
                gap="xs",
            ),
        ],
        gap="sm",
    )

    return dmc.AccordionItem(
        [
            dmc.AccordionControl(header),
            dmc.AccordionPanel(body),
        ],
        value=job.id,
    )

layout = dmc.Container(
    children=[
        dcc.Interval(id="jobs-poll-interval", interval=5000, n_intervals=0, max_intervals=-1),
        dcc.Store(id="jobs-signal"),
        dmc.Title("Running jobs", order=2, mb="md"),
            dmc.ScrollArea(
                html.Div(id="jobs-list"),
                offsetScrollbars=True,
                type="scroll",
        ),
    ],
    fluid=True,
    p="md",
)

@callback(
    Output("jobs-signal", "data"),
    Input("jobs-poll-interval", "n_intervals"),
    State("jobs-signal", "data"),
)
def poll_signal(_, current):
    signal = get_signal()

    if signal == current:
        return no_update

    return signal

@callback(
    Output("jobs-list", "children"),
    Input("jobs-signal", "data"),
)
def update_jobs(_):
    jobs = get_jobs()

    if not jobs:
        return dmc.Alert(
            "There are no running or finished jobs.",
            color="gray",
            variant="light",
        )

    return dmc.Accordion(
        children=[make_job_item(job) for job in jobs],
        multiple=True,
        variant="separated",
        radius="md",
    )

# @callback(
#     Input("jobs-poll-interval", "n_intervals"),
#     prevent_initial_call=True,
# )
# def auto_create_job(n_intervals):
#     create_job()