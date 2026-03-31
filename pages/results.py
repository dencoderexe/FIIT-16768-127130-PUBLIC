from dash import html, dcc, Input, Output, State, callback, clientside_callback
from dash_iconify import DashIconify

import os
import dash
import plotly.graph_objects as go
import dash_mantine_components as dmc

from models.jobs import Job, Step, Status, memory_to_str
from services.job_manager import get_job_by_id, get_brief_report

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
                dmc.TableTh("Max memory usage:", w=160),
                dmc.TableTd(memory_to_str(job.max_memory_usage) or "—"),
            ]),
        ])
    ]

    def format_arg_name(arg: str) -> str:
        match arg:
            case "reference_genome":
                return "Reference genome"
            case "microsatellite_list":
                return "Microsatellite list"
            case "tumor_bam":
                return "Tumor BAM"
            case "normal_bam":
                return "Normal BAM"
            case "bed_file":
                return "BED file"
            case "model":
                return "Model"
            case "output":
                return "Output"
            
            case "threads":
                return "Threads"
            
            case "region":
                return "Region"
            
            case "fdr_threshold":
                return "FDR threshold"
            case "instable_sites_threshold":
                return "Instable sites threshold"
            
            case "coverage":
                return "Coverage"
            case "coverage_normalization":
                return "Coverage normalization"
            
            case "min_homo_size":
                return "Min homopolymer size"
            case "min_homo_size_dist":
                return "Min homopolymer size for distribution analysis"
            case "max_homo_size_dist":
                return "Max homopolymer size for distribution analysis"
            
            case "min_microsat_size":
                return "Min microsatellite size"
            case "min_microsat_size_dist":
                return "Min microsatellite size for distribution analysis"
            case "max_microsat_size_dist":
                return "Max microsatellite size for distribution analysis"
            
            case "span_size_window":
                return "Span size around window for extracting reads"
            
            case "homopolymer_only":
                return "Homopolymer only"
            case "microsatellite_only":
                return "Microsatellite only"
            
            case "include_zero_coverage_sites":
                return "Include zero coverage sites"
            case "out_site_no_read_coverage":
                return "Include sites with no read coverage"
            
            case "min_read_quality":
                return "Min read quality"
            case "min_locus_quality":
                return "Min locus quality"
            case "min_read_length":
                return "Min read length"
            case "min_locus_coverage":
                return "Min locus coverage"
            case "min_repeat_reads":
                return "Min repeat reads"
            case "standard_deviations":
                return "Standard deviations"

            case _:
                return arg.replace("_", " ").capitalize()

    def format_arg_value(arg: str, value):
        if value in (None, "", []):
            return "—"

        match arg:
            case ("homopolymer_only" | "microsatellite_only" | "coverage_normalization" | "write_index" |
                  "include_zero_coverage_sites" | "include-zero-coverage-sites" | "out_site_no_read_coverage"):
                return "Yes" if value == 1 else "No"
            case ("reference_genome" | "microsatellite_list" | "tumor_bam" | "normal_bam" | "bam_file" | "bed_file"):
                return os.path.basename(value)
            case _:
                return value

    run_params = [
        dmc.TableTbody([
            dmc.TableTr([
                dmc.TableTh(format_arg_name(arg), w=160),
                dmc.TableTd(format_arg_value(arg, value) if value is not None else "not selected"),
            ])
            for arg, value in sorted(
                job.args.items(),
                key=lambda x: (
                    x[0] not in ("tumor_bam", "normal_bam", "bed_file", "microsatellite_list"),
                    x[0],
                )
            )
            if arg not in ("output",)
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
            [make_step_row(step) for step in job.steps],
            gap="xs",
        ),
    ]

    def make_section(value: str, title: str, children, icon: str | None = None):
        return dmc.AccordionItem(
            value=value,
            children=[
                dmc.AccordionControl(
                    dmc.Group(
                        gap="sm",
                        children=[
                            DashIconify(icon=icon, height=18) if icon else None,
                            dmc.Text(title, fw=700),
                        ],
                    )
                ),
                dmc.AccordionPanel(
                    loading_block(
                        dmc.Box(children=children, pt="xs")
                    )
                ),
            ],
        )

    return dmc.Container(
        dmc.Accordion(
            chevronPosition="right",
            variant="separated",
            radius="md",
            multiple=True,
            value=["basic-info", "run-params", "brief-output", "steps", "graphs"],
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
                        children=run_params,
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
                        children=make_memory_usage_graph(job),
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