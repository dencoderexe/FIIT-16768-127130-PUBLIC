import os
import zipfile
import dash
import dash_mantine_components as dmc

from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx
from dash_iconify import DashIconify

from services.job_signal import get_signal
from services.job_manager import get_jobs, get_saved_jobs, get_job_by_id, delete_job, Status, Tool, Command, Job, Step

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
        justify="space-between",
        align="center",
        w="100%",
        children=[
            dmc.Group(
                gap="sm",
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
            ),
            *(
                [
                    dmc.Text(
                        step.finished_at.strftime("%d.%m.%Y %H:%M:%S"),
                        size="xs",
                        c="dimmed",
                    )
                ]
                if step.finished_at
                else []
            ),
            *(
                [
                    dmc.Progress(
                        color="yellow",
                        size="md",
                        value=int((step.progress_current / step.progress_total) * 100) if step.progress_total else 0,
                        w=110,
                        animated=True
                    )
                ]
                if not step.finished_at 
                and step.progress_current is not None 
                and step.progress_total is not None
                else []
            ),
        ],
    )

def make_job_actions(job: Job):
    actions = []

    if job.status == Status.SUCCESS:
        actions.append(
            dmc.Button(
                "Log",
                id={"type": "job-log-button", "job_id": job.id},
                variant="light",
                leftSection=DashIconify(icon="bi:file-earmark-text"),
                fullWidth=True,
            )
        )
        actions.append(
            dmc.Button(
                "Output",
                id={"type": "job-output-button", "job_id": job.id},
                variant="light",
                leftSection=DashIconify(icon="bi:download"),
                fullWidth=True,
            ),
        )
        actions.append(
            dmc.Button(
                "Delete",
                id={"type": "job-delete-button", "job_id": job.id},
                variant="subtle",
                color="red",
                leftSection=DashIconify(icon="bi:trash"),
                fullWidth=True,
            ),
        )

    if job.status == Status.FAILED:
        actions.append(
            dmc.Button(
                "Log",
                id={"type": "job-log-button", "job_id": job.id},
                variant="light",
                leftSection=DashIconify(icon="bi:file-earmark-text"),
                fullWidth=True,
            )
        )
        actions.append(
            dmc.Button(
                "Delete",
                id={"type": "job-delete-button", "job_id": job.id},
                variant="subtle",
                color="red",
                leftSection=DashIconify(icon="bi:trash"),
                fullWidth=True,
            ),
        )

    return dmc.Stack(
        gap="xs",
        children=actions,
        w=180,
    )

def make_job_item(job: Job):
    """

    """
    header = dmc.Group(
        children=[
            dmc.Stack(
                [
                    dmc.Text(job.started_at.strftime("%d.%m.%Y %H:%M:%S"), size="xs", c="dimmed"),
                    dmc.Text(job.tool.name, size="sm", fw=600),
                ],
                gap=2,
            ),
            make_status_icon(job.status),
        ],
        justify="space-between",
        align="center",
        w="100%",
    )

    steps_and_actions = dmc.Group(
        align="flex-start",
        justify="space-between",
        w="100%",
        wrap="nowrap",
        children=[
            dmc.Stack(
                [make_step_row(step) for step in job.steps],
                gap="xs",
                style={"flex": 1},
            ),
            make_job_actions(job),
        ],
    )

    body = dmc.Stack(
        children=[
            dmc.Text(job.tool.description, size="sm", c="dimmed"),
            dmc.Divider(),
            steps_and_actions,
            *(
                [
                    dmc.Divider(),
                    dmc.Textarea(
                        value=job.error_message,
                        readOnly=True,
                        maxRows=4,
                        autosize=True,
                        styles={
                            "input": {
                                "borderColor": "red",
                                "color": "#ff6b6b",
                            }
                        }
                    ),
                ]
                if job.error_message != ""
                else []
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

def make_jobs_list(jobs: list[Job], no_jobs_text: str):
    if not jobs:
        return dmc.Alert(
            no_jobs_text,
            color="gray",
            variant="light",
        )

    return dmc.Accordion(
        children=[make_job_item(job) for job in jobs],
        multiple=True,
        variant="separated",
        radius="md",
    )

layout = dmc.Container(
    children=[
        dcc.Interval(id="jobs-poll-interval", interval=1000, n_intervals=0, max_intervals=-1),
        dcc.Store(id="jobs-signal"),
        dcc.Download(id="job-download"),
        dmc.Title("Running jobs", order=2, mb="md"),
        dmc.ScrollArea(
            children=[
                html.Div(id="current-jobs-list"),
                dmc.Divider(label="Previous sessions", labelPosition="center"),
                html.Div(id="saved-jobs-list"),
            ],
            offsetScrollbars=True,
            type="scroll",
        ),
        dcc.Store(id="delete-job-id"),
        dmc.Modal(
            id="delete-job-modal",
            title="Delete job",
            centered=True,
            children=[
                dmc.Text("Are you sure you want to delete this job and all its files??"),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("Cancel", id="delete-job-cancel", variant="outline"),
                        dmc.Button("Delete", id="delete-job-confirm", color="red"),
                    ],
                    justify="flex-end",
                ),
            ],
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
    Output("current-jobs-list", "children"),
    Output("saved-jobs-list", "children"),
    Input("jobs-signal", "data"),
)
def update_jobs(_):
    jobs = get_jobs()
    saved_jobs = get_saved_jobs()

    return [
        make_jobs_list(
            jobs,
            "There are no running or finished jobs.",
        ),
        make_jobs_list(
            saved_jobs,
            "There are no jobs from previous sessions.",
        ),
    ]


@callback(
        Output("notification-container", "sendNotifications", allow_duplicate=True),
        Input("jobs-signal", "data"),
        prevent_initial_call=True,
)
def notify_jobs(_):
    jobs = get_jobs()

    if not jobs:
        return no_update

    for job in jobs:
        if job.notified:
            continue
        
        if job.status == Status.SUCCESS:
            job.notified = True
            return [dict(
                title="Job finished",
                id=f"job-{job.id}",
                action="show",
                color="green",
                message=f"{job.tool.name} finished successfully",
                autoClose=3000,
                icon=DashIconify(icon=Status.SUCCESS.icon),
            )]
        elif job.status == Status.FAILED:
            job.notified = True
            return [dict(
                title="Job failed",
                id=f"job-{job.id}",
                action="show",
                color="red",
                message=f"{job.tool.name} failed",
                autoClose=3000,
                icon=DashIconify(icon=Status.FAILED.icon),
            )]
    return no_update

@callback(
    Output("job-download", "data"),
    Input({"type": "job-log-button", "job_id": ALL}, "n_clicks"),
    Input({"type": "job-output-button", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def download_job_file(log_clicks, output_clicks):
    if not any(log_clicks or []) and not any(output_clicks or []):
        return no_update

    triggered = ctx.triggered_id
    if not triggered:
        return no_update

    job_id = triggered["job_id"]
    button_type = triggered["type"]
    job = get_job_by_id(job_id)

    if not job:
        return no_update

    if button_type == "job-log-button":
        return dcc.send_file(job.log_file)

    if button_type == "job-output-button":
        def write_zip(bytes_io):
            excluded_files = {}
            excluded_extensions = {".log", ".json",
            }
            
            with zipfile.ZipFile(bytes_io, "w", zipfile.ZIP_DEFLATED) as z:
                for file in os.listdir(job.job_dir):
                    full_path = os.path.join(job.job_dir, file)

                    if not os.path.isfile(full_path):
                        continue

                    if file in excluded_files:
                        continue

                    if os.path.splitext(file)[1] in excluded_extensions:
                        continue

                    z.write(full_path, arcname=file)

        return dcc.send_bytes(write_zip, f"{job.id}_output.zip")

    return no_update

@callback(
    Output("delete-job-modal", "opened"),
    Output("delete-job-id", "data"),
    Input({"type": "job-delete-button", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_delete_modal(n_clicks):
    if not n_clicks or not any(n_clicks):
        return no_update, no_update

    triggered = ctx.triggered_id
    if not triggered:
        return no_update, no_update

    return True, triggered["job_id"]

@callback(
    Output("delete-job-modal", "opened", allow_duplicate=True),
    Output("delete-job-id", "data", allow_duplicate=True),
    Input("delete-job-cancel", "n_clicks"),
    prevent_initial_call=True,
)
def close_delete_modal(_):
    return False, None

@callback(
    Output("delete-job-modal", "opened", allow_duplicate=True),
    Output("delete-job-id", "data", allow_duplicate=True),
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("delete-job-confirm", "n_clicks"),
    State("delete-job-id", "data"),
    prevent_initial_call=True,
)
def delete_job_and_files(n_clicks, job_id):
    if not n_clicks:
        return no_update, no_update, no_update

    if not job_id:
        return False, None, no_update

    job = get_job_by_id(job_id)

    if not job:
        return False, None, no_update

    delete_job(job)

    return (
        False,
        None,
        [dict(
            title="Job deleted",
            id=f"job-{job.id}",
            action="show",
            color="grey",
            message=f"{job.tool.name} deleted",
            autoClose=3000,
            icon=DashIconify(icon="bi:trash"),
        )]
    )