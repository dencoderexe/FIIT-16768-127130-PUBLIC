from dash import Input, Output, State, callback, no_update
from dash_iconify import DashIconify

from components.helper import helper
from services.job_manager import create_job
from services.file_manager import get_files

from configs.tools import TOOLS
from configs.paths import data_path

import os
import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/repeatfinder")

tool = TOOLS["repeatfinder"]

def make_repeatfinder():
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
                            dmc.Text("Reference genome file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper(
                                "Select the reference genome file in FASTA format."
                            ),
                        ],
                        gap=6,
                    ),
                    id="repeatfinder-refgenome-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".fasta", ".fas", ".fa", ".fna", ".ffn", ".faa", ".mpfa", ".frn"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select reference genome FASTA file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="repeatfinder-start-button", disabled=True),
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
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum repeat region length (bp)", size="sm", fw=500),
                            helper(
                                "Minimum number of bases a repeat region must span to be reported as a microsatellite.\n"
                                "Example: a region of length 8 bp will be ignored if the threshold is set to 10."
                            ),
                        ],
                        gap=6,
                    ),
                    id="repeatfinder-min-length",
                    value=10,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximum repeat region length (bp)", size="sm", fw=500),
                            helper(
                                "Maximum number of bases a repeat region can span to be reported as a microsatellite.\n"
                                "Example: a region of length 120 bp will be ignored if the threshold is set to 100."
                            ),
                        ],
                        gap=6,
                    ),
                    id="repeatfinder-max-length",
                    value=100,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum k-mer repeats", size="sm", fw=500),
                            helper(
                                "Minimum number of repeated k-mer units required to report a microsatellite.\n"
                                "Example: (AC)2 will be ignored if the threshold is set to 3."
                            ),
                        ],
                        gap=6,
                    ),
                    id="repeatfinder-min-repeats",
                    value=3,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum k-mer length (bp)", size="sm", fw=500),
                            helper(
                                "Minimum length of the repeating motif (k-mer) to consider.\n"
                                "Example: with value 2, single-base repeats like (A)n will be ignored."
                            ),
                        ],
                        gap=6,
                    ),
                    id="repeatfinder-min-kmer",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximum k-mer length (bp)", size="sm", fw=500),
                            helper(
                                "Maximum length of the repeating motif (k-mer) to consider.\n"
                                "Example: with value 5, repeats like (ACGTAC)n will be ignored.\n"
                                "Values >= 6 are not recommended as they may include telomeric repeats."
                            ),
                        ],
                        gap=6,
                    ),
                    id="repeatfinder-max-kmer",
                    value=5,
                    min=1,
                    allowDecimal=False,
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

command_description = dmc.Paper(
    withBorder=True,
    radius="md",
    p="md",
    w="100%",
    children=dmc.Stack(
        [
            dmc.Text(
                tool.commands["repeatfinder"].description,
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
            dmc.Text(tool.description),
            dmc.Group(
                [
                    DashIconify(icon="bi:github", width=18),
                    dmc.Anchor(
                        "View original tool on GitHub",
                        href="https://github.com/OSU-SRLab/MANTIS?tab=readme-ov-file#repeatfinder",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_description,
            make_repeatfinder(),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)
    
@callback(
    Output("repeatfinder-start-button", "disabled"),
    Input("repeatfinder-refgenome-file-select", "value"),
)
def repeatfinder_start_button(refgenome):
    return not bool(refgenome)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("repeatfinder-start-button", "n_clicks"),
    State("repeatfinder-refgenome-file-select", "value"),
    State("repeatfinder-min-length", "value"),
    State("repeatfinder-max-length", "value"),
    State("repeatfinder-min-repeats", "value"),
    State("repeatfinder-min-kmer", "value"),
    State("repeatfinder-max-kmer", "value"),
    prevent_initial_call=True,
)
def repeatfinder_start_job(
    n_clicks,
    reference_genome,
    min_length,
    max_length,
    min_repeats,
    min_kmer,
    max_kmer,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get("repeatfinder"),
            reference_genome=reference_genome,
            output=f"{os.path.splitext(os.path.basename(reference_genome))[0]}.loci.bed",

            min_length=min_length,
            max_length=max_length,
            min_repeats=min_repeats,
            min_kmer=min_kmer,
            max_kmer=max_kmer,
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
    Output("repeatfinder-command-description", "children"),
    Input("repeatfinder-command-select", "value"),
)
def msisensor_command_description(command_key):
    command = tool.commands.get(command_key)
    return command.description if command else "No description available."