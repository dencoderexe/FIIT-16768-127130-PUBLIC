from dash import html, dcc, Input, Output, State, callback, clientside_callback

import dash
import plotly.graph_objects as go
import dash_mantine_components as dmc

from models.jobs import Job, Status, memory_to_str
from services.job_manager import get_job_by_id, get_brief_report
from components.job_arg_table import job_arg_table
from components.step_row import step_row
from components.accordion_section import make_section

dash.register_page(__name__, path_template="/results/<job_id>")

def make_cpu_usage_graph(job):
    history = job.cpu_usage_history

    if not history:
        return []

    x = [entry["Timestamp"] for entry in history]
    y = [entry["CPU"] for entry in history]
    cpu_str = [f"{entry['CPU']:.1f}%" for entry in history]

    max_entry = max(history, key=lambda entry: entry["CPU"])

    fig = go.Figure()

    # cpu usage line
    fig.add_scatter(
        x=x,
        y=y,
        mode="lines",
        name="CPU",
        customdata=cpu_str,
        line=dict(color="#00c853"),
        hovertemplate=(
            "Timestamp: %{x}<br>"
            "CPU: %{customdata}<extra></extra>"
        ),
    )

    # max cpu usage point
    fig.add_scatter(
        x=[max_entry["Timestamp"]],
        y=[max_entry["CPU"]],
        mode="markers",
        name="Max",
        customdata=[f"{max_entry['CPU']:.1f}%"],
        hovertemplate=(
            "MAX<br>"
            "Timestamp: %{x}<br>"
            "CPU: %{customdata}<extra></extra>"
        ),
        marker=dict(
            size=10,
            symbol="circle",
            line=dict(width=2),
            color="#ff9800",
        ),
    )

    fig.update_layout(
        title=dict(
            text="CPU Usage Over Time",
            x=0.5,
            xanchor="center"
        ),
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Timestamp",
        yaxis_title="CPU (%)",
        hovermode="closest",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uirevision=f"cpu-graph-{job.id}",
    )

    return [
        dcc.Graph(
            id="cpu-usage-graph",
            figure=fig,
            config={
                "displayModeBar": "hover",
                "toImageButtonOptions": {
                    "filename": f"cpu_usage_{job.id}",
                },
            },
        ),
    ]

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
            "Timestamp: %{x}<br>"
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
            "Timestamp: %{x}<br>"
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
        xaxis_title="Timestamp",
        yaxis_title="Memory (MiB)",
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

def make_results_content(job: Job):
    basic_info_table = [
        dmc.TableTbody([
            dmc.TableTr([
                dmc.TableTh("Tool:", w=160),
                dmc.TableTd(job.tool.name),
            ]),
            dmc.TableTr([
                dmc.TableTh("Command:", w=160),
                dmc.TableTd(job.command.name if job.tool.key not in ("mantis") else "-"),
            ]),
            dmc.TableTr([
                dmc.TableTh("Mode:", w=160),
                dmc.TableTd(job.get_mode()),
            ]),
            dmc.TableTr([
                dmc.TableTh("Started:", w=160),
                dmc.TableTd(job.started_at.strftime('%d.%m.%Y %H:%M:%S') if job.started_at else "-"),
            ]),
            dmc.TableTr([
                dmc.TableTh("Finished:", w=160),
                dmc.TableTd(job.finished_at.strftime('%d.%m.%Y %H:%M:%S') if job.finished_at else "-"),
            ]),
            dmc.TableTr([
                dmc.TableTh("Duration:", w=160),
                dmc.TableTd(job.get_duration() or "—"),
            ]),
            dmc.TableTr([
                dmc.TableTh("Max CPU usage:", w=160),
                dmc.TableTd(job.max_cpu_usage or "—"),
            ]),
            dmc.TableTr([
                dmc.TableTh("Max RAM usage:", w=160),
                dmc.TableTd(memory_to_str(job.max_memory_usage) or "—"),
            ]),
        ])
    ]

    steps = [
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
            [step_row(step) for step in job.steps],
            gap="xs",
        ),
    ]

    return dmc.Container(
        dmc.Accordion(
            chevronPosition="right",
            variant="separated",
            radius="md",
            multiple=True,
            value=["basic-info", "run-params", "brief-report", "steps", "graphs"],
            children=[
                make_section(
                    "basic-info",
                    "Basic information",
                    dmc.Table(
                        highlightOnHover=True,
                        withTableBorder=True,
                        withColumnBorders=True,
                        variant="vertical",
                        children=basic_info_table,
                    ),
                    icon="bi:info-circle",
                ),
                make_section(
                    "run-params",
                    "Run parameters",
                    dmc.Table(
                        highlightOnHover=True,
                        withTableBorder=True,
                        withColumnBorders=True,
                        variant="vertical",
                        children=job_arg_table(job),
                    ),
                    icon="bi:sliders",
                ),
                make_section(
                    "brief-report",
                    "Brief report",
                    dmc.Textarea(
                        value=get_brief_report(job),
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
                    icon="bi:terminal",
                ),
                make_section(
                    "steps",
                    "Steps",
                    dmc.Stack(
                        w="100%",
                        children=steps,
                    ),
                    icon="bi:list-check",
                ),
                make_section(
                    "graphs",
                    "Graphs",
                    dmc.Stack(
                        gap="md",
                        children=[
                            *make_cpu_usage_graph(job),
                            dmc.Divider(),
                            *make_memory_usage_graph(job),
                        ],
                    ),
                    icon="bi:bar-chart",
                ),
            ],
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

# cpu and memory usage graph theme switch client-side callback
clientside_callback(
    """
    function(checked, cpu_graph, memory_graph) {
        function updateGraphTheme(figure) {
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

        return [
            updateGraphTheme(cpu_graph),
            updateGraphTheme(memory_graph)
        ];
    }
    """,
    Output("cpu-usage-graph", "figure"),
    Output("memory-usage-graph", "figure"),
    Input("color-scheme-toggle", "checked"),
    State("cpu-usage-graph", "figure"),
    State("memory-usage-graph", "figure"),
    prevent_initial_call=False,
)
