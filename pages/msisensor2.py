import os
import dash
import dash_mantine_components as dmc

from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx
from dash_iconify import DashIconify

from services.job_manager import TOOLS, Job, create_job
from services.file_manager import root_path, get_files, get_dirs
from components.helper import helper

dash.register_page(__name__, path="/msisensor2")

tool = TOOLS["msisensor2"]

def make_msi():
    required_options = dmc.Paper(
        withBorder=True,
        radius="md",
        p="md",
        h="100%",
        children=dmc.Stack(
            [
                dmc.Title("Required options", order=4),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Model", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper(""),
                        ],
                        gap=6,
                    ),
                    id="model-select",
                    data=[
                        {"value": "models_b37_HumanG1Kv37", "label": "b37 (HumanG1Kv37)"},
                        {"value": "models_hg19_GRCh37", "label": "hg19 / GRCh37"},
                        {"value": "models_hg38", "label": "hg38 / GRCh38"},
                    ],
                    allowDeselect=False,
                    checkIconPosition="right",
                    placeholder="Select model",
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Tumor .BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper(""),
                        ],
                        gap=6,
                    ),
                    id="bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(root_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select .BAM file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                dmc.Button("Start", id="start-button", disabled=True),
            ],
            gap="md",
            justify="space-between",
            h="100%",
        ),
    )

    additional_options = dmc.Paper(
        withBorder=True,
        radius="md",
        p="md",
        h="100%",
        children=dmc.Stack(
            [
                dmc.Title("Additional options", order=4),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Coverage", size="sm", fw=500),
                            helper(""),
                        ],
                        gap=6,
                    ),
                    id="coverage-select",
                    value="20",
                    data=[
                        {"value": "20", "label": "WXS: 20"},
                        {"value": "15", "label": "WGS: 15"},
                    ],
                    allowDeselect=False,
                    checkIconPosition="right",
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Threads", size="sm", fw=500),
                            helper(""),
                        ],
                        gap=6,
                    ),
                    id="threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Homopolymer only", size="sm", fw=500),
                            helper(""),
                        ],
                        gap=6,
                    ),
                    id="homopolymer-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Microsatellite only", size="sm", fw=500),
                            helper(""),
                        ],
                        gap=6,
                    ),
                    id="microsatellite-only",
                    checked=False,
                ),
            ],
            gap="md",
            h="100%",
        ),
    )

    return dmc.Grid(
        [
            dmc.GridCol(required_options, span=6),
            dmc.GridCol(additional_options, span=6),
        ],
        gutter="md",
        align="stretch",
    )

command_select = dmc.Paper(
    withBorder=True,
    radius="md",
    p="md",
    w="100%",
    children=dmc.Stack(
        [
            dmc.Title("Command", order=4),
            dmc.Select(
                label="Select command",
                placeholder="Select one",
                id="command-select",
                value="msi",
                data=[
                    {"value": command.key, "label": command.name}
                    for command in tool.commands.values()
                ],
                allowDeselect=False,
            ),
        ],
        gap="xs",
    ),
)

layout = dmc.Container(
    dmc.Stack(
        [
            dmc.Title(tool.name, order=2),
            dmc.Text(tool.description),
            dmc.Group(
                [
                    DashIconify(icon="bi:github", width=18),
                    dmc.Anchor(
                        "View on GitHub",
                        href="https://github.com/niu-lab/msisensor2",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_select,
            html.Div(id="command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("command-container", "children"), 
    Input("command-select", "value"),
)
def select_command(value):
    if value == "msi":
        return make_msi()
    else:
        return None
    
@callback(
    Output("start-button", "disabled"),
    Input("model-select", "value"),
    Input("bam-file-select", "value"),
)
def toggle_start_button(model, tumor_bam):
    return not (model and tumor_bam)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("start-button", "n_clicks"),
    State("command-select", "value"),
    State("model-select", "value"),
    State("bam-file-select", "value"),
    State("coverage-select", "value"),
    State("threads", "value"),
    State("homopolymer-only", "checked"),
    State("microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def start_job(
    n_clicks,
    command_key,
    model,
    tumor_bam,
    coverage,
    threads,
    homopolymer_only,
    microsatellite_only,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            model=model,
            tumor_bam=tumor_bam,
            output=os.path.splitext(os.path.basename(tumor_bam))[0],
            coverage=coverage,
            threads=threads,
            homopolymer_only=int(bool(homopolymer_only)),
            microsatellite_only=int(bool(microsatellite_only)),
        )

        return [dict(
            title="Job started",
            action="show",
            color="yellow",
            message=f"{tool.name} started",
            autoClose=3000,
            icon=DashIconify(icon="bi:arrow-repeat"),
        )]

    except Exception as e:
        return [dict(
            title="Failed to start job",
            action="show",
            color="red",
            message=str(e),
            autoClose=4000,
            icon=DashIconify(icon="bi:x-circle-fill"),
        )]
    
@callback(
    Output("homopolymer-only", "checked"),
    Output("microsatellite-only", "checked"),
    Input("homopolymer-only", "checked"),
    Input("microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def homopolymer_microsatellite_only_switch(homopolymer_only, microsatellite_only):
    triggered = ctx.triggered_id

    if triggered == "homopolymer-only" and homopolymer_only:
        return True, False

    if triggered == "microsatellite-only" and microsatellite_only:
        return False, True

    return homopolymer_only, microsatellite_only