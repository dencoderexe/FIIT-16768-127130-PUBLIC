import os
import dash
import dash_mantine_components as dmc

from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx
from dash_iconify import DashIconify

from services.job_manager import TOOLS, Job, create_job
from services.file_manager import root_path, get_files, get_dirs
from components.helper import helper

dash.register_page(__name__, path="/msisensor")

tool = TOOLS["msisensor"]

def make_scan():
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
                            helper("Reference genome sequences file in .fasta format"),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-refgenome-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(root_path, "")}
                        for file in get_files(extensions=[".fasta", ".fas", ".fa", ".fna", ".ffn", ".faa", ".mpfa", ".frn"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select reference genome FASTA file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="msisensor-scan-start-button", disabled=True),
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
                            dmc.Text("Minimal homopolymer size", size="sm", fw=500),
                            helper("Minimal homopolymer size"),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-min-homo-size",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal homopolymer size", size="sm", fw=500),
                            helper("Maximal homopolymer size"),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-max-homo-size",
                    value=50,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Context length", size="sm", fw=500),
                            helper("Context length"),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-context-length",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximum length of microsatellite", size="sm", fw=500),
                            helper("Maximal length of microsatellite"),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-max-microsat-len",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal microsatellite repeats", size="sm", fw=500),
                            helper("Minimal repeat times of microsatellite"),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-min-microsat-rep",
                    value=3,
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
                    id="msisensor-scan-homopolymer-only",
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

def make_msi():
    return
# def make_msi():
#     required_options = dmc.Paper(
#         withBorder=True,
#         radius="md",
#         p="md",
#         h="100%",
#         children=dmc.Stack(
#             [
#                 dmc.Title("Required options", order=4),
#                 dmc.Select(
#                     label=dmc.Group(
#                         [
#                             dmc.Text("Model", size="sm", fw=500),
#                             dmc.Text("*", c="red", size="sm", fw=700),
#                             helper(""),
#                         ],
#                         gap=6,
#                     ),
#                     id="model-select",
#                     data=[
#                         {"value": "models_b37_HumanG1Kv37", "label": "b37 (HumanG1Kv37)"},
#                         {"value": "models_hg19_GRCh37", "label": "hg19 / GRCh37"},
#                         {"value": "models_hg38", "label": "hg38 / GRCh38"},
#                     ],
#                     allowDeselect=False,
#                     checkIconPosition="right",
#                     placeholder="Select model",
#                 ),
#                 dmc.Select(
#                     label=dmc.Group(
#                         [
#                             dmc.Text("Tumor .BAM file", size="sm", fw=500),
#                             dmc.Text("*", c="red", size="sm", fw=700),
#                             helper(""),
#                         ],
#                         gap=6,
#                     ),
#                     id="bam-file-select",
#                     data=[
#                         {"value": str(file), "label": str(file).replace(root_path, "")}
#                         for file in get_files(extensions=[".bam"])
#                     ],
#                     nothingFoundMessage="Nothing found",
#                     checkIconPosition="right",
#                     placeholder="Select .BAM file",
#                     searchable=True,
#                 ),
#                 dmc.Space(h="xl"),
#                 dmc.Button("Start", id="start-button", disabled=True),
#             ],
#             gap="md",
#             justify="space-between",
#             h="100%",
#         ),
#     )

#     additional_options = dmc.Paper(
#         withBorder=True,
#         radius="md",
#         p="md",
#         h="100%",
#         children=dmc.Stack(
#             [
#                 dmc.Title("Additional options", order=4),
#                 dmc.Select(
#                     label=dmc.Group(
#                         [
#                             dmc.Text("Coverage", size="sm", fw=500),
#                             helper(""),
#                         ],
#                         gap=6,
#                     ),
#                     id="coverage-select",
#                     value="20",
#                     data=[
#                         {"value": "20", "label": "WXS: 20"},
#                         {"value": "15", "label": "WGS: 15"},
#                     ],
#                     allowDeselect=False,
#                     checkIconPosition="right",
#                 ),
#                 dmc.NumberInput(
#                     label=dmc.Group(
#                         [
#                             dmc.Text("Threads", size="sm", fw=500),
#                             helper(""),
#                         ],
#                         gap=6,
#                     ),
#                     id="threads",
#                     value=1,
#                     min=1,
#                     allowDecimal=False,
#                 ),
#                 dmc.Switch(
#                     label=dmc.Group(
#                         [
#                             dmc.Text("Homopolymer only", size="sm", fw=500),
#                             helper(""),
#                         ],
#                         gap=6,
#                     ),
#                     id="homopolymer-only",
#                     checked=False,
#                 ),
#                 dmc.Switch(
#                     label=dmc.Group(
#                         [
#                             dmc.Text("Microsatellite only", size="sm", fw=500),
#                             helper(""),
#                         ],
#                         gap=6,
#                     ),
#                     id="microsatellite-only",
#                     checked=False,
#                 ),
#             ],
#             gap="md",
#             h="100%",
#         ),
#     )

#     return dmc.Grid(
#         [
#             dmc.GridCol(required_options, span=6),
#             dmc.GridCol(additional_options, span=6),
#         ],
#         gutter="md",
#         align="stretch",
#     )

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
                id="msisensor-command-select",
                value="scan",
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
                        href="https://github.com/ding-lab/msisensor",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_select,
            html.Div(id="msisensor-command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("msisensor-command-container", "children"), 
    Input("msisensor-command-select", "value"),
)
def select_command(value):
    if value == "scan":
        return make_scan()
    elif value == "msi":
        return make_msi()
    else:
        return None
    
@callback(
    Output("msisensor-scan-start-button", "disabled"),
    Input("msisensor-scan-refgenome-file-select", "value"),
)
def msisensor_scan_start_button(refgenome):
    return not bool(refgenome)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor-scan-start-button", "n_clicks"),
    State("msisensor-command-select", "value"),
    State("msisensor-scan-refgenome-file-select", "value"),
    State("msisensor-scan-min-homo-size", "value"),
    State("msisensor-scan-max-homo-size", "value"),
    State("msisensor-scan-context-length", "value"),
    State("msisensor-scan-max-microsat-len", "value"),
    State("msisensor-scan-min-microsat-rep", "value"),
    State("msisensor-scan-homopolymer-only", "checked"),
    prevent_initial_call=True,
)
def msisensor_scan_start_job(
    n_clicks,
    command_key,
    reference_genome,
    min_homo_size,
    max_homo_size,
    context_length,
    max_microsat_len,
    min_microsat_rep,
    homopolymer_only,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            reference_genome=reference_genome,
            output=f"{os.path.splitext(os.path.basename(reference_genome))[0]}.microsatellite.list",
            min_homo_size=min_homo_size,
            max_homo_size=max_homo_size,
            context_length=context_length,
            max_microsat_len=max_microsat_len,
            min_microsat_rep=min_microsat_rep,
            homopolymer_only=int(bool(homopolymer_only)),
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