from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx, clientside_callback
from dash_iconify import DashIconify

from services.job_signal import get_active_jobs_signal, get_finished_jobs_signal
from services.job_manager import get_active_jobs, get_finished_jobs, get_job_by_id, delete_job, terminate_job_process
from services.file_manager import write_zip
from models.jobs import Status, Step, Job, memory_to_str

import dash
import logging
import dash_mantine_components as dmc

logger = logging.getLogger(__name__)

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
    return dmc.Grid(
        align="center",
        children=[
            dmc.GridCol(
                dmc.Group(
                    gap="sm",
                    wrap="nowrap",
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
                span=6,
            ),
            dmc.GridCol(
                dmc.Text(
                    step.started_at.strftime("%d.%m.%Y %H:%M:%S") if step.started_at else "-",
                    size="xs",
                    c="dimmed",
                ),
                span=3,
                style={"textAlign": "center"},
            ),
            dmc.GridCol(
                dmc.Group(
                    gap="xs",
                    justify="center",
                    wrap="nowrap",
                    children=[
                        *(
                            [
                                dmc.Progress(
                                    color="yellow",
                                    size="md",
                                    value=int((step.progress_current / step.progress_total) * 100) if step.progress_total else 0,
                                    w=110,
                                    animated=True,
                                )
                            ]
                            if not step.finished_at
                            and step.progress_current is not None
                            and step.progress_total is not None
                            else [
                                dmc.Text(
                                    step.finished_at.strftime("%d.%m.%Y %H:%M:%S") if step.finished_at else "-",
                                    size="xs",
                                    c="dimmed",
                                ),
                            ]
                        ),
                    ],
                ),
                span=3,
            ),
        ],
    )

def make_job_actions(job: Job):
    actions = []

    if job.status == Status.RUNNING or job.status == Status.PENDING:
        actions.append(
            dmc.Button(
                "Stop",
                id={"type": "job-stop-button", "job_id": job.id},
                variant="subtle",
                color="red",
                leftSection=DashIconify(icon="bi:x-octagon-fill"),
                fullWidth=True,
            )
        )
    elif job.status == Status.FAILED:
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
    elif job.command.key not in {"msi", "mantis"}:
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
                id={"type": "job-output-too-big-button", "job_id": job.id},
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
    elif job.status == Status.SUCCESS:
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
    else:
        return

    return dmc.Stack(
        gap="xs",
        children=actions,
        w=180,
        align="stretch",
    )

def make_job_item(job: Job):
    """

    """
    header = dmc.Stack(
        gap=4,
        children=[
            dmc.Grid(
                children=[
                    dmc.GridCol(
                        dmc.Text(
                            f"{job.started_at.strftime("%d.%m.%Y %H:%M:%S")} - {job.finished_at.strftime("%d.%m.%Y %H:%M:%S")}" 
                            if job.finished_at 
                            else f"{job.started_at.strftime("%d.%m.%Y %H:%M:%S")}",
                            size="xs",
                            c="dimmed",
                        ), 
                        span=5,
                    ), 
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Output", size="xs", c="dimmed")), 
                        span=2,
                    ), 
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Duration", size="xs", c="dimmed")), 
                        span=2,
                    ), 
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Memory usage" if job.status not in (Status.SUCCESS, Status.FAILED) else "Max. memory usage", size="xs", c="dimmed")), 
                        span=2,
                    ),
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Status", size="xs", c="dimmed")), 
                        span=1,
                    ),
                ],
            ),

            dmc.Grid(
                align="center",
                children=[
                    dmc.GridCol(
                        dmc.Stack(
                            [
                                
                                *(
                                    [dmc.Text(f"{job.tool.name} [{job.command.name}]", size="sm", fw=600)]
                                    if job.command.key in ("msi", "scan", "pro", "index", "merge", "faidx")
                                    else [dmc.Text(f"{job.tool.name}", size="sm", fw=600)]
                                ),
                            ],
                            gap=2,
                        ),
                        span=5,
                    ),
                     dmc.GridCol(
                        dmc.Center(
                            dmc.Text(job.args.get("output", "-"), size="xs", c="dimmed")
                        ),
                        span=2,
                    ),
                    dmc.GridCol(
                        dmc.Center(
                            dmc.Text(job.get_duration() or "—", size="xs", c="dimmed")
                        ),
                        span=2,
                    ),
                    dmc.GridCol(
                        dmc.Center(
                            dmc.Text(
                                memory_to_str(
                                    (
                                        job.current_memory_usage 
                                        if job.status not in (Status.SUCCESS, Status.FAILED) 
                                        else job.max_memory_usage
                                    )
                                ) or "—",
                                size="xs",
                                c="dimmed",
                            )
                        ),
                        span=2,
                    ),
                    dmc.GridCol(
                        dmc.Center(make_status_icon(job.status)),
                        span=1,
                    ),
                ],
            ),
        ],
    )

    steps_and_actions = dmc.Group(
        align="flex-start",
        justify="space-between",
        w="100%",
        wrap="nowrap",
        children=[
            dmc.Stack(
                w="100%",
                children=[
                    dmc.Grid(
                        children=[
                            dmc.GridCol(
                                dmc.Text("Step:", size="sm", c="dimmed"), 
                                span=6,
                            ),
                            dmc.GridCol(
                                dmc.Text("Started at:", size="sm", c="dimmed"), 
                                span=3, 
                                style={"textAlign": "center"},
                            ),
                            dmc.GridCol(
                                dmc.Text("Finished at:", size="sm", c="dimmed"), 
                                span=3, 
                                style={"textAlign": "center"},
                            ),
                        ],
                    ),
                    dmc.Stack(
                        [make_step_row(step) for step in job.steps],
                        gap="xs",
                    ),
                ],
            ),
            make_job_actions(job),
        ],
    )

    error_message = (
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
    )

    results = (
        [
            dmc.Divider(),
            dcc.Link(
                dmc.Button(
                    "Open results",
                    variant="light",
                    color="green",
                    fullWidth=True,
                ),
                href=f"/results/{job.id}",
                style={"textDecoration": "none"},
            ),
        ]
        if job.status == Status.SUCCESS and job.command.key in ("msi", "mantis", "pro")
        else []
    )

    body = dmc.Stack(
        children=[
            dmc.Divider(),
            steps_and_actions,
            *results,
            *error_message,
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
        dcc.Interval(id="jobs-poll-interval", interval=2500, n_intervals=0, max_intervals=-1),
        dcc.Store(id="active-jobs-signal"),
        dcc.Store(id="finished-jobs-signal"),
        dcc.Store(id="opened-job-ids", data=[]),

        dmc.Title("Jobs", order=2, mb="md"),

        dmc.ScrollArea(
            children=[
                dmc.Divider(label="Active jobs", labelPosition="center"),
                dmc.Accordion(
                    id="active-jobs-accordion",
                    multiple=True,
                    variant="separated",
                    radius="md",
                    children=[],
                    value=[],
                ),
                html.Div(id="active-jobs-empty-text"),
                dmc.Divider(label="Finished jobs", labelPosition="center"),
                dmc.Accordion(
                    id="finished-jobs-accordion",
                    multiple=True,
                    variant="separated",
                    radius="md",
                    children=[],
                    value=[],
                ),
                html.Div(id="finished-jobs-empty-text"),
            ],
            offsetScrollbars=True,
            type="scroll",
        ),
        
        dcc.Store(id="download-busy", data=False),
        dcc.Download(id="job-download"),
        dcc.Store(id="job-output-too-big-id"),
        dmc.Modal(
            id="job-output-too-big-modal",
            title="Job output is too big",
            centered=True,
            children=[
                dmc.Text("Job output is too big to be downloaded, please ask administrator if you really need those files."),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("Ok", id="job-output-too-big-ok", color="green"),
                    ],
                    justify="flex-end",
                ),
            ],
        ),

        dcc.Store(id="delete-job-id"),
        dmc.Modal(
            id="delete-job-modal",
            title="Delete job",
            centered=True,
            children=[
                dmc.Text("Are you sure you want to delete this job and all its files?"),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("No", id="delete-job-cancel", variant="outline"),
                        dmc.Button("Yes", id="delete-job-confirm", color="red"),
                    ],
                    justify="flex-end",
                ),
            ],
        ),

        dcc.Store(id="stop-job-id"),
        dmc.Modal(
            id="stop-job-modal",
            title="Stop job",
            centered=True,
            children=[
                dmc.Text("Are you sure you want to stop this job?"),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("No", id="stop-job-no", variant="outline"),
                        dmc.Button("Yes", id="stop-job-yes", color="red"),
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
    Output("active-jobs-signal", "data"),
    Output("finished-jobs-signal", "data"),
    Input("jobs-poll-interval", "n_intervals"),
    State("active-jobs-signal", "data"),
    State("finished-jobs-signal", "data"),
)
def poll_jobs_signals(_, current_active_jobs_signal, current_finished_jobs_signal):
    active_jobs_signal = get_active_jobs_signal()
    finished_jobs_signal = get_finished_jobs_signal()
    return (
        active_jobs_signal if active_jobs_signal != current_active_jobs_signal else no_update,
        finished_jobs_signal if finished_jobs_signal != current_finished_jobs_signal else no_update,
    )

@callback(
    Output("active-jobs-accordion", "children"),
    Output("active-jobs-accordion", "value"),
    Output("active-jobs-empty-text", "children"),
    Input("active-jobs-signal", "data"),
    State("opened-job-ids", "data"),
)
def render_active_jobs(_, opened_job_ids):
    jobs = get_active_jobs()
    opened_job_ids = set(opened_job_ids or [])

    if not jobs:
        return (
            [], 
            [], 
            dmc.Alert(
                "There are no active jobs.",
                color="gray",
                variant="light",
            ),
        )

    return (
        [make_job_item(job) for job in jobs],
        [job.id for job in jobs if job.id in opened_job_ids],
        None,
    )

@callback(
    Output("finished-jobs-accordion", "children"),
    Output("finished-jobs-accordion", "value"),
    Output("finished-jobs-empty-text", "children"),
    Input("finished-jobs-signal", "data"),
    State("opened-job-ids", "data"),
)
def render_finished_jobs(_, opened_job_ids):
    jobs = get_finished_jobs()
    opened_job_ids = set(opened_job_ids or [])

    if not jobs:
        return (
            [], 
            [], 
            dmc.Alert(
                "There are no finished jobs.",
                color="gray",
                variant="light",
            ),
        )

    return (
        [
            make_job_item(job)
            for job in jobs
        ],
        [job.id for job in jobs if job.id in opened_job_ids],
        None,
    )

@callback(
    Output("opened-job-ids", "data"),
    Input("active-jobs-accordion", "value"),
    Input("finished-jobs-accordion", "value"),
    State("opened-job-ids", "data"),
    prevent_initial_call=True,
)
def update_opened_jobs(active_value, finished_value, stored):
    active_value = set(active_value or [])
    finished_value = set(finished_value or [])
    stored = set(stored or [])

    active_ids = {job.id for job in get_active_jobs()}
    finished_ids = {job.id for job in get_finished_jobs()}
    visible_now = active_ids | finished_ids

    triggered = ctx.triggered_id

    result = stored & visible_now

    if triggered == "active-jobs-accordion":
        result -= active_ids
        result |= active_value

    elif triggered == "finished-jobs-accordion":
        result -= finished_ids
        result |= finished_value

    return list(result)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("finished-jobs-signal", "data"),
    prevent_initial_call=True,
)
def notify_jobs(_):
    jobs = get_finished_jobs()

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

clientside_callback(
    """
    function(n_clicks_list) {
        const no_update = window.dash_clientside.no_update;

        if (!n_clicks_list || !Array.isArray(n_clicks_list)) {
            return [no_update, no_update];
        }

        const hasClick = n_clicks_list.some(v => (v || 0) > 0);
        if (!hasClick) {
            return [no_update, no_update];
        }

        const ctx = window.dash_clientside.callback_context;
        const triggered = ctx.triggered_id;

        if (!triggered || !triggered.job_id) {
            return [no_update, no_update];
        }

        return [true, triggered.job_id];
    }
    """,
    Output("delete-job-modal", "opened"),
    Output("delete-job-id", "data"),
    Input({"type": "job-delete-button", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        return [false, null];
    }
    """,
    Output("delete-job-modal", "opened", allow_duplicate=True),
    Output("delete-job-id", "data", allow_duplicate=True),
    Input("delete-job-cancel", "n_clicks"),
    prevent_initial_call=True,
)

@callback(
    Output("active-jobs-signal", "data", allow_duplicate=True),
    Output("finished-jobs-signal", "data", allow_duplicate=True),
    Output("delete-job-modal", "opened", allow_duplicate=True),
    Output("delete-job-id", "data", allow_duplicate=True),
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("delete-job-confirm", "n_clicks"),
    State("delete-job-id", "data"),
    State("active-jobs-signal", "data"),
    State("finished-jobs-signal", "data"),
    prevent_initial_call=True,
)
def delete_job_and_files(n_clicks, job_id, active_jobs_signal, finished_jobs_signal):
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update

    if not job_id:
        return no_update, no_update, False, None, no_update

    job = get_job_by_id(job_id)

    if not job:
        logger.warning("[job:%s] Delete requested from UI, but job was not found", job_id)
        return no_update, no_update, False, None, no_update

    logger.info("[job:%s] Delete requested from UI", job.id)
    delete_job(job)

    return (
        active_jobs_signal + 1,
        finished_jobs_signal + 1,
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

clientside_callback(
    """
    function(n_clicks_list) {
        const no_update = window.dash_clientside.no_update;

        if (!n_clicks_list || !Array.isArray(n_clicks_list)) {
            return [no_update, no_update];
        }

        const hasClick = n_clicks_list.some(v => (v || 0) > 0);
        if (!hasClick) {
            return [no_update, no_update];
        }

        const ctx = window.dash_clientside.callback_context;
        const triggered = ctx.triggered_id;

        if (!triggered || !triggered.job_id) {
            return [no_update, no_update];
        }

        return [true, triggered.job_id];
    }
    """,
    Output("stop-job-modal", "opened"),
    Output("stop-job-id", "data"),
    Input({"type": "job-stop-button", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function(n_clicks) {
        const no_update = window.dash_clientside.no_update;

        if (!n_clicks) {
            return [no_update, no_update];
        }

        return [false, null];
    }
    """,
    Output("stop-job-modal", "opened", allow_duplicate=True),
    Output("stop-job-id", "data", allow_duplicate=True),
    Input("stop-job-no", "n_clicks"),
    prevent_initial_call=True,
)

@callback(
    Output("active-jobs-signal", "data", allow_duplicate=True),
    Output("finished-jobs-signal", "data", allow_duplicate=True),
    Output("stop-job-modal", "opened", allow_duplicate=True),
    Output("stop-job-id", "data", allow_duplicate=True),
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("stop-job-yes", "n_clicks"),
    State("stop-job-id", "data"),
    State("active-jobs-signal", "data"),
    State("finished-jobs-signal", "data"),
    prevent_initial_call=True,
)
def stop_job(n_clicks, job_id, active_jobs_signal, finished_jobs_signal):
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update

    if not job_id:
        return no_update, no_update, False, None, no_update

    job = get_job_by_id(job_id)

    if not job:
        logger.warning("[job:%s] Stop requested from UI, but job was not found", job_id)
        return no_update, no_update, False, None, no_update

    logger.warning("[job:%s] Stop requested from UI", job.id)
    job.terminated = True
    terminate_job_process(job)

    return (
        active_jobs_signal + 1,
        finished_jobs_signal + 1,
        False,
        None,
        [dict(
            title="Job stopped",
            id=f"job-{job.id}",
            action="show",
            color="grey",
            message=f"{job.tool.name} stopped",
            autoClose=3000,
            icon=DashIconify(icon="bi:x-octagon-fill"),
        )]
    )

clientside_callback(
    """
    function(n_clicks_list) {
        const no_update = window.dash_clientside.no_update;

        if (!n_clicks_list || !Array.isArray(n_clicks_list)) {
            return [no_update, no_update];
        }

        const hasClick = n_clicks_list.some(v => (v || 0) > 0);
        if (!hasClick) {
            return [no_update, no_update];
        }

        const ctx = window.dash_clientside.callback_context;
        const triggered = ctx.triggered_id;

        if (!triggered || !triggered.job_id) {
            return [no_update, no_update];
        }

        return [true, triggered.job_id];
    }
    """,
    Output("job-output-too-big-modal", "opened", allow_duplicate=True),
    Output("job-output-too-big-id", "data", allow_duplicate=True),
    Input({"type": "job-output-too-big-button", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function(n_clicks) {
        const no_update = window.dash_clientside.no_update;

        if (!n_clicks) {
            return [no_update, no_update];
        }

        return [false, null];
    }
    """,
    Output("job-output-too-big-modal", "opened", allow_duplicate=True),
    Output("job-output-too-big-id", "data", allow_duplicate=True),
    Input("job-output-too-big-ok", "n_clicks"),
    prevent_initial_call=True,
)

@callback(
    Output("job-download", "data"),
    Input({"type": "job-log-button", "job_id": ALL}, "n_clicks"),
    Input({"type": "job-output-button", "job_id": ALL}, "n_clicks"),
    prevent_initial_call=True,
    running=[(Output("download-busy", "data"), True, False)],
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
        logger.warning("[job:%s] Download requested, but job was not found", job_id)
        return no_update

    if button_type == "job-log-button":
        logger.info("[job:%s] Downloading job log", job.id)
        return dcc.send_file(job.log_file)

    if button_type == "job-output-button":
        logger.info("[job:%s] Downloading job output archive", job.id)
        return dcc.send_bytes(lambda bytes_io: write_zip(job.job_dir, bytes_io), f"{job.tool.name}_{job.command.name}_output.zip")

    return no_update

clientside_callback(
    """
    function(busy, logIds, outputIds) {
        const isBusy = !!busy;
        const logs = logIds || [];
        const outputs = outputIds || [];

        return [
            Array(logs.length).fill(isBusy),     // log loading
            Array(outputs.length).fill(isBusy),  // output loading
            Array(logs.length).fill(isBusy),     // log disabled
            Array(outputs.length).fill(isBusy),  // output disabled
        ];
    }
    """,
    Output({"type": "job-log-button", "job_id": ALL}, "loading"),
    Output({"type": "job-output-button", "job_id": ALL}, "loading"),
    Output({"type": "job-log-button", "job_id": ALL}, "disabled"),
    Output({"type": "job-output-button", "job_id": ALL}, "disabled"),
    Input("download-busy", "data"),
    State({"type": "job-log-button", "job_id": ALL}, "id"),
    State({"type": "job-output-button", "job_id": ALL}, "id"),
)