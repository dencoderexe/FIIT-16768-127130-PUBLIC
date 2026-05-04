from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx, clientside_callback
from dash_iconify import DashIconify

from services.job_signal import get_active_jobs_signal, get_finished_jobs_signal
from services.job_manager import get_active_jobs, get_finished_jobs, get_job_by_id, delete_job, terminate_job_process
from services.file_manager import get_job_archive, is_file_empty, is_job_archive_too_big
from models.jobs import Status, Job, memory_to_str
from components.status_icon import status_icon
from components.step_row import step_row
from components.helper import helper
from components.accordion_section import make_section

from configs.tools import msi_analysis_commands

import math
import dash
import logging
import dash_mantine_components as dmc

FINISHED_JOBS_PAGE_SIZE = 10

logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/jobs")

def make_stop_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Stop",
        id={"type": "job-stop-button", "job_id": job.id},
        variant="subtle",
        color="red",
        size="md",
        leftSection=DashIconify(icon="bi:x-octagon-fill"),
        fullWidth=True,
    )

def make_log_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Log",
        id={"type": "job-log-button", "job_id": job.id},
        variant="light",
        size="md",
        leftSection=DashIconify(icon="bi:file-earmark-text"),
        fullWidth=True,
    )

def make_empty_log_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Log",
        id={"type": "job-empty-log-button", "job_id": job.id},
        variant="light",
        size="md",
        leftSection=DashIconify(icon="bi:file-earmark-text"),
        fullWidth=True,
    )

def make_output_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Output",
        id={"type": "job-output-button", "job_id": job.id},
        variant="light",
        size="md",
        leftSection=DashIconify(icon="bi:download"),
        fullWidth=True,
    )

def make_output_too_big_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Output",
        id={"type": "job-output-too-big-button", "job_id": job.id},
        variant="light",
        size="md",
        leftSection=DashIconify(icon="bi:download"),
        fullWidth=True,
    )

def make_output_preparing_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Output",
        id={"type": "job-output-preparing-button", "job_id": job.id},
        variant="light",
        size="md",
        leftSection=DashIconify(icon="bi:download"),
        fullWidth=True,
        loading=True,
        disabled=True,
    )

def make_delete_button(job: Job) -> dmc.Button:
    return dmc.Button(
        "Delete",
        id={"type": "job-delete-button", "job_id": job.id},
        variant="subtle",
        size="md",
        color="red",
        leftSection=DashIconify(icon="bi:trash"),
        fullWidth=True,
    )

def make_job_actions(job: Job):
    if job.status == Status.RUNNING or job.status == Status.PENDING:
        actions = [
            make_stop_button(job)
        ]
    elif job.status == Status.FAILED:
        actions = [
            make_log_button(job) if not is_file_empty(job.log_file) else make_empty_log_button(job),
            make_delete_button(job),
        ]
    elif job.status == Status.SUCCESS:
        archive_path = get_job_archive(job.job_dir)

        if archive_path is None:
            output_button = make_output_preparing_button(job)
        elif is_job_archive_too_big(job.job_dir):
            output_button = make_output_too_big_button(job)
        else:
            output_button = make_output_button(job)

        actions = [
            make_log_button(job) if not is_file_empty(job.log_file) else make_empty_log_button(job),
            output_button,
            make_delete_button(job),
        ]
    else:
        return []

    return dmc.Stack(
        gap="sm",
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
                            size="sm",
                            c="dimmed",
                        ), 
                        span=5,
                    ), 
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Output", size="sm")), 
                        span=3,
                    ), 
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Duration", size="sm")), 
                        span=1,
                    ), 
                    dmc.GridCol(
                        dmc.Center(dmc.Text("CPU usage" if job.status not in (Status.SUCCESS, Status.FAILED) else "Max. CPU usage", size="sm")), 
                        span=1,
                    ),
                    dmc.GridCol(
                        dmc.Center(dmc.Text("RAM usage" if job.status not in (Status.SUCCESS, Status.FAILED) else "Max. RAM usage", size="sm")), 
                        span=1,
                    ),
                    dmc.GridCol(
                        dmc.Center(dmc.Text("Status", size="sm")), 
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
                                dmc.Group(
                                    children = [
                                        dmc.Text(f"{job.tool.name} [{job.command.name}]", size="md", fw=600)
                                        if len(job.tool.commands.keys()) > 1
                                        else dmc.Text(f"{job.tool.name}", size="md", fw=600),
                                        helper(job),
                                    ]
                                ),
                                

                                dmc.Text(job.get_mode(), size="sm", c="dimmed")
                                if job.command.key in msi_analysis_commands and job.tool.key != "mslist-converter"
                                else None,
                            ],
                            gap=2,
                        ),
                        span=5,
                    ),
                     dmc.GridCol(
                        dmc.Center(
                            dmc.Text(job.args.get("output", "-"), size="sm", c="dimmed")
                        ),
                        span=3,
                    ),
                    dmc.GridCol(
                        dmc.Center(
                            dmc.Text(job.get_duration() or "—", size="sm", c="dimmed")
                        ),
                        span=1,
                    ),
                    dmc.GridCol(
                        dmc.Center(
                            dmc.Text(
                                f"{round(cpu_usage, 2)} %"
                                if (
                                    cpu_usage := (
                                        job.current_cpu_usage
                                        if job.current_cpu_usage is not None and job.status not in (Status.SUCCESS, Status.FAILED)
                                        else job.max_cpu_usage
                                    )
                                ) is not None
                                else "—",
                                size="sm",
                                c="dimmed",
                            )
                        ),
                        span=1,
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
                                size="sm",
                                c="dimmed",
                            )
                        ),
                        span=1,
                    ),
                    dmc.GridCol(
                        dmc.Center(status_icon(job.status)),
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
                                dmc.Text("Step:", size="md"), 
                                span=6,
                            ),
                            dmc.GridCol(
                                dmc.Text("Started at:", size="md"), 
                                span=3, 
                                style={"textAlign": "center"},
                            ),
                            dmc.GridCol(
                                dmc.Text("Finished at:", size="md"), 
                                span=3, 
                                style={"textAlign": "center"},
                            ),
                        ],
                    ),
                    dmc.Stack(
                        [step_row(step) for step in job.steps],
                        gap="sm",
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
                size="md",
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
                    size="md",
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
        gap="md",
    )

    return dmc.AccordionItem(
        [
            dmc.AccordionControl(header),
            dmc.AccordionPanel(body),
        ],
        value=job.id,
    )

filters = dmc.SimpleGrid(
    cols={"base": 1, "md": 2, "lg": 4},
    spacing="sm",
    children=[
        dmc.MultiSelect(
            label="Filter by tool",
            id="jobs-tool-filter",
            placeholder="Select tools",
            data=[],
            size="md",
            clearable=True,
            searchable=True,
        ),
        dmc.MultiSelect(
            label="Filter by command",
            id="jobs-command-filter",
            placeholder="Select commands",
            data=[],
            size="md",
            clearable=True,
            searchable=True,
        ),
        dmc.MultiSelect(
            label="Filter by output",
            id="jobs-output-filter",
            placeholder="Select output",
            data=[],
            size="md",
            clearable=True,
            searchable=True,
        ),
        dmc.MultiSelect(
            label="Filter by job status",
            id="jobs-status-filter",
            placeholder="Select status",
            data=[],
            size="md",
            clearable=True,
            searchable=True,
        ),
    ],
)

def make_status_legend():
    return dmc.Group(
        gap="lg",
        mb="md",
        children=[
            dmc.Text("Job/Step status:", size="md"),
            *[
                dmc.Group(
                    gap="sm",
                    children=[
                        status_icon(status),
                        dmc.Text(status.name.title(), size="md"),
                    ],
                )
                for status in Status
            ],
        ],
    )

def filter_jobs(
    jobs: list[Job],
    selected_tools,
    selected_commands,
    selected_outputs,
    selected_statuses,
) -> list[Job]:
    selected_tools = selected_tools or []
    selected_commands = selected_commands or []
    selected_outputs = selected_outputs or []
    selected_statuses = selected_statuses or []

    return [
        job for job in jobs
        if (not selected_tools or job.tool.name in selected_tools)
        and (not selected_commands or job.command.name in selected_commands)
        and (not selected_outputs or job.args.get("output", "-") in selected_outputs)
        and (not selected_statuses or job.status.name in selected_statuses)
    ]

layout = dmc.Container(
    children=[
        dcc.Interval(id="jobs-poll-interval", interval=2500, n_intervals=0, max_intervals=-1),
        dcc.Store(id="active-jobs-signal"),
        dcc.Store(id="finished-jobs-signal"),

        dmc.Title("Jobs", order=2, mb="md"),

        dmc.Accordion(
            chevronPosition="right",
            variant="separated",
            radius="md",
            multiple=True,
            # value=["introduction", "legend", "job-filters"],
            children=[
                make_section(
                    "introduction",
                    "Introduction",
                    dmc.Text(
                        "This page provides a centralized overview of all submitted jobs, allowing you to "
                        "monitor their execution, inspect results, and manage job lifecycle.\n"
                        "\n"
                        "Jobs are automatically grouped into active and finished categories. Each job entry contains detailed information, "
                        "including running parameters, execution time, resource usage (CPU and RAM), status, and step-by-step progress. "
                        "You can expand any job to view its internal steps, access logs, download outputs, or perform actions such as stopping or deleting the job.\n"
                        "\n"
                        "The page updates automatically, so you can track running processes in near real time without manual refresh. "
                        "Filters are available to help you quickly locate specific jobs based on tool, command, output, or status.\n"
                        "\n"
                        "For completed jobs, additional actions become available:\n"
                        "- View logs to inspect execution details or errors.\n"
                        "- Download output files as an archive.\n"
                        "- Open the results page for further analysis (only available for MSI analysis tools).\n"
                        "\n"
                        "Please note:\n"
                        "- The Results page is only available for MSI analysis tools. Preprocessing tools do not generate a results view.\n"
                        "- Output files can be downloaded directly only if their size does not exceed the configured limit (250 MB). "
                        "If the output is larger, you will be prompted to contact the administrator to retrieve the data.\n"
                        "\n"
                        "Use this page as the main control panel for managing and reviewing all analysis workflows.\n",
                        style={"whiteSpace": "pre-line"},
                        size="md",
                    ),
                    icon="bi:info-circle",
                ),
                make_section(
                    "legend",
                    "Legend",
                    make_status_legend(),
                    icon="bi:question-circle",
                ),
                make_section(
                    "job-filters",
                    "Filters",
                    filters,
                    icon="bi:funnel",
                ),
            ],
        ),

        dmc.Divider(label="Active jobs", labelPosition="center"),
        dmc.Box(
            pos="relative",
            style={"minHeight": "50px"},
            children=[
                dmc.LoadingOverlay(
                    id="loading-overlay-active-jobs",
                    visible=False,
                    overlayProps={"radius": "sm", "blur": 2},
                    loaderProps={"type": "oval", "size": "md"},
                    zIndex=10,
                ),
                dmc.Accordion(
                    id="active-jobs-accordion",
                    multiple=True,
                    variant="separated",
                    radius="md",
                    children=[],
                    value=[],
                ),
                html.Div(id="active-jobs-empty-text"),
            ],
        ),

        dmc.Divider(label="Finished jobs", labelPosition="center"),
        dmc.Box(
            pos="relative",
            style={"minHeight": "50px"},
            children=[
                dmc.LoadingOverlay(
                    id="loading-overlay-finished-jobs",
                    visible=False,
                    overlayProps={"radius": "sm", "blur": 2},
                    loaderProps={"type": "oval", "size": "md"},
                    zIndex=10,
                ),
                dmc.Accordion(
                    id="finished-jobs-accordion",
                    multiple=True,
                    variant="separated",
                    radius="md",
                    children=[],
                    value=[],
                ),
                html.Div(id="finished-jobs-empty-text"),
                dmc.Group(
                    justify="center",
                    mt="md",
                    children=[
                        dcc.Store(id="finished-jobs-page", data=1),
                        dmc.Pagination(
                            id="finished-jobs-pagination",
                            total=1,
                            value=1,
                            withEdges=True,
                            siblings=1,
                        )
                    ],
                ),
            ],
        ),
        
        dcc.Store(id="download-busy", data=False),
        dcc.Download(id="job-download"),
        dcc.Store(id="job-empty-log-id"),
        dmc.Modal(
            id="job-empty-log-modal",
            title=dmc.Text("Empty log file", size="lg", fw=600),
            centered=True,
            children=[
                dmc.Text("This job log file is empty, so there is nothing to download.", size="lg"),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("Ok", id="job-empty-log-ok", color="green", size="md"),
                    ],
                    justify="flex-end",
                ),
            ],
        ),
        dcc.Store(id="job-output-too-big-id"),
        dmc.Modal(
            id="job-output-too-big-modal",
            title=dmc.Text("Output is too large", size="lg", fw=600),
            centered=True,
            children=[
                dmc.Text("This job output is too large to download from the web interface.", size="lg"),
                dmc.Text(
                    "If you still need these files, please contact the administrator.",
                    c="dimmed",
                    size="md",
                    mt="sm",
                ),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("Ok", id="job-output-too-big-ok", color="green", size="md"),
                    ],
                    justify="flex-end",
                ),
            ],
        ),

        dcc.Store(id="delete-job-id"),
        dmc.Modal(
            id="delete-job-modal",
            title=dmc.Text("Delete job", size="lg", fw=600),
            centered=True,
            children=[
                dmc.Text("Are you sure you want to delete this job?", size="lg"),
                dmc.Text(
                    "All job files will be permanently removed.",
                    c="dimmed",
                    size="md",
                    mt="sm",
                ),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("No", id="delete-job-cancel", variant="outline", size="md"),
                        dmc.Button("Yes", id="delete-job-confirm", color="red", size="md"),
                    ],
                    justify="flex-end",
                ),
            ],
        ),

        dcc.Store(id="stop-job-id"),
        dmc.Modal(
            id="stop-job-modal",
            title=dmc.Text("Stop job", size="lg", fw=600),
            centered=True,
            children=[
                dmc.Text("Are you sure you want to stop this job?", size="lg"),
                dmc.Text(
                    "The running process will be terminated.",
                    c="dimmed",
                    size="md",
                    mt="sm",
                ),
                dmc.Space(h=15),
                dmc.Group(
                    [
                        dmc.Button("No", id="stop-job-no", variant="outline", size="md"),
                        dmc.Button("Yes", id="stop-job-yes", color="red", size="md"),
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
    Output("active-jobs-empty-text", "children"),
    Input("active-jobs-signal", "data"),
    Input("jobs-tool-filter", "value"),
    Input("jobs-command-filter", "value"),
    Input("jobs-output-filter", "value"),
    Input("jobs-status-filter", "value"),
)
def render_active_jobs(_, selected_tools, selected_commands, selected_outputs, selected_statuses):
    jobs = get_active_jobs()
    jobs = filter_jobs(
        jobs,
        selected_tools,
        selected_commands,
        selected_outputs,
        selected_statuses,
    )

    if not jobs:
        return (
            [], 
            dmc.Alert(
                "There are no active jobs matching the selected filters.",
                color="gray",
                variant="light",
                fz="md",
            ),
        )

    return (
        [make_job_item(job) for job in jobs],
        None,
    )

@callback(
    Output("finished-jobs-accordion", "children"),
    Output("finished-jobs-empty-text", "children"),
    Output("finished-jobs-pagination", "total"),
    Output("finished-jobs-pagination", "value"),
    Input("finished-jobs-signal", "data"),
    Input("jobs-tool-filter", "value"),
    Input("jobs-command-filter", "value"),
    Input("jobs-output-filter", "value"),
    Input("jobs-status-filter", "value"),
    Input("finished-jobs-pagination", "value"),
    running=[
        (Output("loading-overlay-finished-jobs", "visible"), True, False),
    ],
)
def render_finished_jobs(
    _,
    selected_tools,
    selected_commands,
    selected_outputs,
    selected_statuses,
    page,
):
    page = page or 1

    jobs = get_finished_jobs()
    jobs = filter_jobs(
        jobs,
        selected_tools,
        selected_commands,
        selected_outputs,
        selected_statuses,
    )

    if not jobs:
        return (
            [],
            dmc.Alert(
                "There are no finished jobs matching the selected filters.",
                color="gray",
                variant="light",
                fz="md",
            ),
            1,
            1,
        )

    total_pages = max(1, math.ceil(len(jobs) / FINISHED_JOBS_PAGE_SIZE))

    if page > total_pages:
        page = total_pages

    start = (page - 1) * FINISHED_JOBS_PAGE_SIZE
    end = start + FINISHED_JOBS_PAGE_SIZE
    visible_jobs = jobs[start:end]

    return (
        [make_job_item(job) for job in visible_jobs],
        None,
        total_pages,
        page,
    )

@callback(
    Output("jobs-tool-filter", "data"),
    Output("jobs-command-filter", "data"),
    Output("jobs-output-filter", "data"),
    Output("jobs-status-filter", "data"),
    Input("active-jobs-signal", "data"),
    Input("finished-jobs-signal", "data"),
)
def update_filter_options(_, __):
    jobs = get_active_jobs() + get_finished_jobs()

    tool_options = sorted({job.tool.name for job in jobs})
    command_options = sorted({job.command.name for job in jobs if len(job.args) > 1})
    output_options = sorted({job.args.get("output", "-") for job in jobs})
    status_options = [status.name for status in Status]

    return (
        [{"value": tool, "label": tool} for tool in tool_options],
        [{"value": command, "label": command} for command in command_options],
        [{"value": output, "label": output} for output in output_options],
        [{"value": status, "label": status.title()} for status in status_options],
    )

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
    Output("job-empty-log-modal", "opened", allow_duplicate=True),
    Output("job-empty-log-id", "data", allow_duplicate=True),
    Input({"type": "job-empty-log-button", "job_id": ALL}, "n_clicks"),
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
    Output("job-empty-log-modal", "opened", allow_duplicate=True),
    Output("job-empty-log-id", "data", allow_duplicate=True),
    Input("job-empty-log-ok", "n_clicks"),
    prevent_initial_call=True,
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
        archive_path = get_job_archive(job.job_dir)

        if archive_path is None:
            logger.warning("[job:%s] Archive requested, but archive is not ready", job.id)
            return no_update

        logger.info("[job:%s] Downloading job output archive", job.id)

        return dcc.send_file(
            archive_path,
            filename=f"{job.tool.name}_{job.command.name}_output.zip",
        )

    return no_update

# blocks download buttons and sets them as “loading” during any download to prevent downloads from overlapping
clientside_callback(
    """
    function(busy, logIds, emptyLogIds, outputIds, tooBigOutputIds, deleteIds) {
        const isBusy = !!busy;

        const logs = logIds || [];
        const emptyLogs = emptyLogIds || [];
        const outputs = outputIds || [];
        const tooBigOutputs = tooBigOutputIds || [];
        const deletes = deleteIds || [];

        return [
            Array(logs.length).fill(isBusy),
            Array(emptyLogs.length).fill(isBusy),
            Array(outputs.length).fill(isBusy),
            Array(tooBigOutputs.length).fill(isBusy),
            Array(deletes.length).fill(isBusy),

            Array(logs.length).fill(isBusy),
            Array(emptyLogs.length).fill(isBusy),
            Array(outputs.length).fill(isBusy),
            Array(tooBigOutputs.length).fill(isBusy),
            Array(deletes.length).fill(isBusy),
        ];
    }
    """,
    Output({"type": "job-log-button", "job_id": ALL}, "loading"),
    Output({"type": "job-empty-log-button", "job_id": ALL}, "loading"),
    Output({"type": "job-output-button", "job_id": ALL}, "loading"),
    Output({"type": "job-output-too-big-button", "job_id": ALL}, "loading"),
    Output({"type": "job-delete-button", "job_id": ALL}, "loading"),

    Output({"type": "job-log-button", "job_id": ALL}, "disabled"),
    Output({"type": "job-empty-log-button", "job_id": ALL}, "disabled"),
    Output({"type": "job-output-button", "job_id": ALL}, "disabled"),
    Output({"type": "job-output-too-big-button", "job_id": ALL}, "disabled"),
    Output({"type": "job-delete-button", "job_id": ALL}, "disabled"),

    Input("download-busy", "data"),
    State({"type": "job-log-button", "job_id": ALL}, "id"),
    State({"type": "job-empty-log-button", "job_id": ALL}, "id"),
    State({"type": "job-output-button", "job_id": ALL}, "id"),
    State({"type": "job-output-too-big-button", "job_id": ALL}, "id"),
    State({"type": "job-delete-button", "job_id": ALL}, "id"),
    prevent_initial_call=True,
)
