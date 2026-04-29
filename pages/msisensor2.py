from dash import Input, Output, State, callback, no_update, ctx
from dash_iconify import DashIconify

from components.helper import helper
from components.notifications import job_started_notification, job_started_failed_notification
from services.job_manager import create_job
from services.file_manager import get_files, get_dirs, build_output_name

from configs.tools import TOOLS
from configs.paths import data_path, BAM_EXT, MSISENSOR2_MODELS

import os
import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/msisensor2")

tool = TOOLS["msisensor2"]

def make_msi():
    main_options = dmc.Paper(
        withBorder=True,
        radius="md",
        p="md",
        h="100%",
        children=dmc.Stack(
            [
                dmc.Title("Main options", order=4),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Model", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper(
                                "Reference model used for MSI analysis. "
                                "Select the model matching the genome build of your data."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-model-select",
                    data=[
                        {"value": str(dir), "label": str(dir).replace(data_path, "")}
                        for dir in get_dirs(extensions=MSISENSOR2_MODELS)
                    ],
                    allowDeselect=False,
                    checkIconPosition="right",
                    placeholder="Select model",
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Tumor BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the BAM file for the tumor sample."),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-tumor-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=BAM_EXT)
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select BAM file",
                    searchable=True,
                ),

                dmc.Box(style={"flexGrow": 1}),

                dmc.TextInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Output file name", size="sm", fw=500),
                            helper("Optional. Enter a custom output file name without extension."),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-output-name-input",
                    placeholder="Leave empty to use the default file name",
                ),

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
                                helper(
                                    "Minimum sequencing depth threshold used for analysis.\n"
                                    "Recommended defaults are 20 for WXS and 15 for WGS."
                                ),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-coverage",
                    value="15",
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
                            helper(
                                "Number of threads to use for analysis."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Homopolymer only", size="sm", fw=500),
                            helper(
                                "Restrict the analysis to homopolymer loci only."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-homopolymer-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Microsatellite only", size="sm", fw=500),
                            helper(
                                "Restrict the analysis to microsatellite loci only."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor2-msi-microsatellite-only",
                    checked=False,
                ),
            ],
            gap="md",
            h="100%",
        ),
    )

    return dmc.Grid(
        [
            dmc.GridCol(main_options, span=6),
            dmc.GridCol(additional_options, span=6),
        ],
        gutter="md",
        align="stretch",
    )

command_description = dmc.Paper(
    withBorder=True,
    radius="md",
    p="md",
    w="100%",
    children=dmc.Stack(
        [
            dmc.Text(
                tool.commands["msi"].description,
                style={"whiteSpace": "pre-line"},
            ),
        ],
        gap="xs",
    ),
)

layout = dmc.Container(
    dmc.Stack(
        [
            dmc.Title(tool.name, order=2),
            dmc.Text(
                tool.description,
                style={"whiteSpace": "pre-line"},
            ),
            dmc.Group(
                [
                    DashIconify(icon="bi:github", width=18),
                    dmc.Anchor(
                        "View original tool on GitHub",
                        href="https://github.com/niu-lab/msisensor2",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_description,
            make_msi(),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("msisensor2-msi-start-button", "disabled"),
    Input("msisensor2-msi-model-select", "value"),
    Input("msisensor2-msi-tumor-bam-file-select", "value"),
)
def msisensor2_msi_start_button(model, tumor_bam):
    return not all([model, tumor_bam])

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor2-msi-start-button", "n_clicks"),
    State("msisensor2-msi-model-select", "value"),
    State("msisensor2-msi-tumor-bam-file-select", "value"),
    State("msisensor2-msi-coverage", "value"),
    State("msisensor2-msi-threads", "value"),
    State("msisensor2-msi-homopolymer-only", "checked"),
    State("msisensor2-msi-microsatellite-only", "checked"),
    State("msisensor2-msi-output-name-input", "value"),
    prevent_initial_call=True,
)
def msisensor2_msi_start_job(
    n_clicks,
    model,
    tumor_bam,

    coverage,
    threads,
    homopolymer_only,
    microsatellite_only,
    output_name,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get("msi"),
            model=model,
            tumor_bam=tumor_bam,
            output=build_output_name(os.path.splitext(os.path.basename(tumor_bam))[0], output_name, None),
            
            coverage=coverage,
            threads=threads,
            homopolymer_only=int(bool(homopolymer_only)),
            microsatellite_only=int(bool(microsatellite_only)),
        )

        return job_started_notification(f"{tool.name} msi started")

    except Exception as e:
        return job_started_failed_notification(e)
    
@callback(
    Output("msisensor2-msi-homopolymer-only", "checked"),
    Output("msisensor2-msi-microsatellite-only", "checked"),
    Input("msisensor2-msi-homopolymer-only", "checked"),
    Input("msisensor2-msi-microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def msisensor2_msi_homopolymer_microsatellite_only_switch(homopolymer_only, microsatellite_only):
    triggered = ctx.triggered_id

    if triggered == "msisensor2-msi-homopolymer-only" and homopolymer_only:
        return True, False

    if triggered == "msisensor2-msi-microsatellite-only" and microsatellite_only:
        return False, True

    return homopolymer_only, microsatellite_only
