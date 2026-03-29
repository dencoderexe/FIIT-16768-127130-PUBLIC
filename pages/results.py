from dash import html, dcc, Input, Output, State, callback, clientside_callback
from dash_iconify import DashIconify

import dash
import plotly.graph_objects as go
import dash_mantine_components as dmc

from models.jobs import Job, Step, Status, memory_to_str
from services.job_manager import get_job_by_id, get_brief_output

dash.register_page(__name__, path_template="/results/<job_id>")

def make_status_icon(status: Status):
    return dmc.ThemeIcon(
        DashIconify(icon=status.icon, height=18),
        color=status.color,
        variant="light",
        radius="xl",
        size="md",
    )

def make_memory_usage_graph(job):
    history = job.memory_usage_history

    if not history:
        return []

    x = [entry["Timestamp"] for entry in history]
    y = [entry["Memory"] / (1024 ** 2) for entry in history]
    memory_str = [memory_to_str(entry["Memory"]) for entry in history]

    max_entry = max(history, key=lambda entry: entry["Memory"])

    fig = go.Figure()

    # memory usage line
    fig.add_scatter(
        x=x,
        y=y,
        mode="lines",
        name="Memory",
        customdata=memory_str,
        line=dict(color="#0062ff"),
        hovertemplate=(
            "Time: %{x}<br>"
            "Memory: %{customdata}<extra></extra>"
        ),
    )

    # max memory usage point
    fig.add_scatter(
        x=[max_entry["Timestamp"]],
        y=[max_entry["Memory"] / (1024 ** 2)],
        mode="markers",
        name="Max",
        customdata=[memory_to_str(max_entry["Memory"])],
        hovertemplate=(
            "MAX<br>"
            "Time: %{x}<br>"
            "Memory: %{customdata}<extra></extra>"
        ),
        marker=dict(
            size=10,
            symbol="circle",
            line=dict(width=2),
            color="#ff0000",
        ),
    )

    fig.update_layout(
        title=dict(
            text="Memory Usage Over Time",
            x=0.5,
            xanchor="center"
        ),
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Time",
        yaxis_title="MiB",
        hovermode="closest",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uirevision=f"memory-graph-{job.id}",
    )

    return [
        dcc.Graph(
            id="memory-usage-graph",
            figure=fig,
            config={"displayModeBar": "hover",
                    "toImageButtonOptions": {
                        "filename": f"memory_usage_{job.id}",
                    },
            },
        ),
    ]

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
                dmc.Text(
                    step.finished_at.strftime("%d.%m.%Y %H:%M:%S") if step.finished_at else "-",
                    size="xs",
                    c="dimmed",
                ),
                span=3,
                style={"textAlign": "center"},
            ),
        ],
    )

def loading_block(children):
    return dcc.Loading(
        type="circle",
        delay_show=150,
        overlay_style={"visibility":"visible", "filter": "blur(2px)"},
        children=html.Div(children)
    )

def make_results_content(job: Job):
    return dmc.Container(
        dmc.Stack(
            children=[
                loading_block(
                    dmc.Paper(
                        p="md",
                        radius="md",
                        withBorder=True,
                        children=[
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Text("Basic information", fw=800),
                                    dmc.Divider(),
                                    dmc.Text(f"Tool: {job.tool.name}"),
                                    dmc.Text(f"Command: {job.command.name}" if job.tool.key not in ("mantis") else f"Command: -"),
                                    dmc.Text(f"Started: {job.started_at.strftime('%d.%m.%Y %H:%M:%S')}" if job.started_at else "Started: -"),
                                    dmc.Text(f"Finished: {job.finished_at.strftime('%d.%m.%Y %H:%M:%S')}" if job.finished_at else "Finished: -"),
                                    dmc.Text(f"Duration: {job.get_duration() or '—'}"),
                                    dmc.Text(f"Max memory usage: {memory_to_str(job.max_memory_usage) or '—'}"),
                                ],
                            )
                        ],
                    ),
                ),
                loading_block(
                    dmc.Paper(
                        p="md",
                        radius="md",
                        withBorder=True,
                        children=[
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Text("Brief output", fw=800),
                                    dmc.Divider(),
                                    dmc.Textarea(
                                        value=get_brief_output(job),
                                        readOnly=True,
                                        autosize=True,
                                        variant="default",
                                        styles={
                                            "input": {
                                                "fontFamily": "monospace",
                                                "whiteSpace": "pre-wrap",
                                                "wordBreak": "break-word",
                                            }
                                        },
                                    ),
                                ],
                            )
                        ],
                    ),
                ),
                loading_block(
                    dmc.Paper(
                        p="md",
                        radius="md",
                        withBorder=True,
                        children=[
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Text("Steps", fw=800),
                                    dmc.Divider(),
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
                                ],
                            )
                        ],
                    ),
                ),
                loading_block(
                    dmc.Paper(
                        p="md",
                        radius="md",
                        withBorder=True,
                        children=[
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Text("Graphs", fw=800),
                                    dmc.Divider(),
                                    *make_memory_usage_graph(job),
                                ],
                            )
                        ],
                    ),
                ),
            ],
            gap="md",
        ),
        fluid=True,
        p="md",
    )

def layout(job_id=None):
    job = get_job_by_id(job_id)
    if job is None or job.status != Status.SUCCESS:
        return dcc.Location(pathname="/not_found", id="redirect")

    return dmc.Container(
        [
            dcc.Store(id="results-job-id", data=job_id),
            dmc.Title(f"Job results", order=2),
            make_results_content(job),
        ],
        fluid=True,
        p="md",
    )

clientside_callback(
    """
    function(checked, figure) {
        if (!figure) {
            return window.dash_clientside.no_update;
        }

        const newFigure = JSON.parse(JSON.stringify(figure));
        newFigure.layout = newFigure.layout || {};
        newFigure.layout.xaxis = newFigure.layout.xaxis || {};
        newFigure.layout.yaxis = newFigure.layout.yaxis || {};

        if (checked) {
            newFigure.layout.paper_bgcolor = "rgba(0,0,0,0)";
            newFigure.layout.plot_bgcolor = "rgba(0,0,0,0)";
            newFigure.layout.font = {color: "#ffffff"};
            newFigure.layout.xaxis.gridcolor = "rgba(255,255,255,0.08)";
            newFigure.layout.yaxis.gridcolor = "rgba(255,255,255,0.08)";
            newFigure.layout.xaxis.zerolinecolor = "rgba(255,255,255,0.12)";
            newFigure.layout.yaxis.zerolinecolor = "rgba(255,255,255,0.12)";
        } else {
            newFigure.layout.paper_bgcolor = "rgba(0,0,0,0)";
            newFigure.layout.plot_bgcolor = "rgba(0,0,0,0)";
            newFigure.layout.font = {color: "#000000"};
            newFigure.layout.xaxis.gridcolor = "rgba(0,0,0,0.08)";
            newFigure.layout.yaxis.gridcolor = "rgba(0,0,0,0.08)";
            newFigure.layout.xaxis.zerolinecolor = "rgba(0,0,0,0.12)";
            newFigure.layout.yaxis.zerolinecolor = "rgba(0,0,0,0.12)";
        }

        return newFigure;
    }
    """,
    Output("memory-usage-graph", "figure"),
    Input("color-scheme-toggle", "checked"),
    State("memory-usage-graph", "figure"),
    prevent_initial_call=True,
)