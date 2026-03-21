from dash import Input, Output, State, callback, html, no_update, ctx
from dash_iconify import DashIconify

from components.helper import helper
from services.job_manager import create_job
from services.file_manager import get_files

from configs.tools import TOOLS
from configs.paths import data_path

import os
import dash
import dash_mantine_components as dmc

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
                    id="msisensor2-model-select",
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
                    id="msisensor2-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select BAM file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),

                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="msisensor2-msi-start-button", disabled=True),
            ],
            gap="md",
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
                            helper("Coverage threshold for MSI analysis"),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-coverage-select",
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
                            helper("Threads number for parallel computing"),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Homopolymer only", size="sm", fw=500),
                            helper("Output homopolymer only"),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-homopolymer-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Microsatellite only", size="sm", fw=500),
                            helper("Output microsatellite only"),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-microsatellite-only",
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
                id="msisensor2-command-select",
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
            html.Div(id="msisensor2-command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("msisensor2-command-container", "children"), 
    Input("msisensor2-command-select", "value"),
)
def select_command(value):
    if value == "msi":
        return make_msi()
    else:
        return None
    
@callback(
    Output("msisensor2-msi-start-button", "disabled"),
    Input("msisensor2-model-select", "value"),
    Input("msisensor2-bam-file-select", "value"),
)
def msisensor2_msi_start_button(model, tumor_bam):
    return not (model and tumor_bam)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor2-msi-start-button", "n_clicks"),
    State("msisensor2-command-select", "value"),
    State("msisensor2-model-select", "value"),
    State("msisensor2-bam-file-select", "value"),
    State("msisensor2-coverage-select", "value"),
    State("msisensor2-threads", "value"),
    State("msisensor2-homopolymer-only", "checked"),
    State("msisensor2-microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def msisensor2_msi_start_job(
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
            autoClose=3000,
            icon=DashIconify(icon="bi:x-circle-fill"),
        )]
    
@callback(
    Output("msisensor2-homopolymer-only", "checked"),
    Output("msisensor2-microsatellite-only", "checked"),
    Input("msisensor2-homopolymer-only", "checked"),
    Input("msisensor2-microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def homopolymer_microsatellite_only_switch(homopolymer_only, microsatellite_only):
    triggered = ctx.triggered_id

    if triggered == "msisensor2-homopolymer-only" and homopolymer_only:
        return True, False

    if triggered == "msisensor2-microsatellite-only" and microsatellite_only:
        return False, True

    return homopolymer_only, microsatellite_only