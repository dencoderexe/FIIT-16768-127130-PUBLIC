from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx
from dash_iconify import DashIconify

from components.helper import helper
from services.job_manager import create_job
from services.file_manager import get_files

from configs.tools import TOOLS
from configs.paths import data_path

import os
import re
import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/msisensor-pro")

tool = TOOLS["msisensor-pro"]

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
                            helper("Select the reference genome file in FASTA format."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-refgenome-file-select",
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

                dmc.Button("Start", id="msisensor-pro-scan-start-button", disabled=True),
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
                            dmc.Text("Minimal homopolymer size", size="sm", fw=500),
                            helper("Set the minimum homopolymer length to include in the scan."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-min-homo-size",
                    value=8,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal homopolymer size", size="sm", fw=500),
                            helper("Set the maximum homopolymer length to include in the scan."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-max-homo-size",
                    value=50,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Context length", size="sm", fw=500),
                            helper("Set the number of flanking bases to include as sequence context."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-context-length",
                    placeholder="5-32",
                    value=5,
                    min=5,
                    max=32,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal length of microsatellite", size="sm", fw=500),
                            helper("Set the maximum microsatellite motif length to include in the scan."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-max-microsat-len",
                    placeholder="1-32",
                    value=6,
                    min=1,
                    max=32,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal repeat times of microsatellite", size="sm", fw=500),
                            helper("Set the minimum number of repeat units required for a microsatellite to be included."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-min-microsat-rep",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Homopolymer only", size="sm", fw=500),
                            helper("Limit the output to homopolymer sites only."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-scan-homopolymer-only",
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
                            dmc.Text("Homopolymer and microsatellite list file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the file containing homopolymer and microsatellite sites."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-microsat-list-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".pro.microsatellite.list"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select microsatellite list file",
                    searchable=True,
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Normal BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the BAM file for the matched normal sample."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-normal-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select normal BAM file",
                    searchable=True,
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
                    id="msisensor-pro-msi-tumor-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select tumor BAM file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="msisensor-pro-msi-start-button", disabled=True),
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
                # dmc.Select(
                #     label=dmc.Group(
                #         [
                #             dmc.Text("Reference genome file", size="sm", fw=500),
                #             helper("Select an optional reference genome file."),
                #         ],
                #         gap=6,
                #     ),
                #     id="msisensor-pro-msi-refgenome-file-select",
                #     data=[
                #         {"value": str(file), "label": str(file).replace(data_path, "")}
                #         for file in get_files(extensions=[".fasta", ".fas", ".fa", ".fna", ".ffn", ".faa", ".mpfa", ".frn"])
                #     ],
                #     nothingFoundMessage="Nothing found",
                #     checkIconPosition="right",
                #     placeholder="Select reference genome FASTA file",
                #     searchable=True,
                # ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Coverage", size="sm", fw=500),
                            helper("Select the recommended coverage threshold for the input data type."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-coverage",
                    value="15",
                    data=[
                        {"value": "20", "label": "WXS: 20"},
                        {"value": "15", "label": "WGS: 15"},
                    ],
                    allowDeselect=False,
                    checkIconPosition="right",
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Coverage normalization", size="sm", fw=500),
                            helper("Enable coverage normalization for paired tumor-normal data."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-coverage-normalization",
                    checked=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("FDR threshold", size="sm", fw=500),
                            helper("Set the false discovery rate threshold for calling somatic unstable sites."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-fdr-threshold",
                    value=0.05,
                    min=0,
                    step=0.01,
                    decimalScale=2,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal homopolymer size for distribution analysis", size="sm", fw=500),
                            helper("Set the minimum homopolymer length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-min-homo-size-dist",
                    value=8,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal homopolymer size for distribution analysis", size="sm", fw=500),
                            helper("Set the maximum homopolymer length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-max-homo-size-dist",
                    value=50,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal microsatellite size for distribution analysis", size="sm", fw=500),
                            helper("Set the minimum microsatellite length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-min-microsat-size-dist",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal microsatellite size for distribution analysis", size="sm", fw=500),
                            helper("Set the maximum microsatellite length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-max-microsat-size-dist",
                    value=40,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Span size around window", size="sm", fw=500),
                            helper("Set the window size around each site for read extraction."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-span-size-window",
                    value=500,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Threads", size="sm", fw=500),
                            helper("Specify the number of threads to use for the analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Homopolymer only", size="sm", fw=500),
                            helper("Limit the output to homopolymer sites only."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-homopolymer-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Microsatellite only", size="sm", fw=500),
                            helper("Limit the output to microsatellite sites only."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-microsatellite-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Include sites with no read coverage", size="sm", fw=500),
                            helper("Include sites with no read coverage in the output ."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-msi-include-zero-coverage-sites",
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

def make_pro():
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
                            dmc.Text("Homopolymer and microsatellite list file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the file containing homopolymer and microsatellite sites."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-microsat-list-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".pro.microsatellite.list"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select microsatellite list file",
                    searchable=True,
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
                    id="msisensor-pro-pro-tumor-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select tumor BAM file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="msisensor-pro-pro-start-button", disabled=True),
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
                            dmc.Text("Minimal threshold for unstable sites detection", size="sm", fw=500),
                            helper("Set the minimum threshold for unstable site detection in tumor-only data."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-instable-sites-threshold",
                    value=0.1,
                    min=0,
                    step=0.01,
                    decimalScale=2,
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Coverage", size="sm", fw=500),
                            helper("Select the recommended coverage threshold for the input data type."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-coverage",
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
                            dmc.Text("Minimal homopolymer size for distribution analysis", size="sm", fw=500),
                            helper("Set the minimum homopolymer length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-min-homo-size-dist",
                    value=8,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal homopolymer size for distribution analysis", size="sm", fw=500),
                            helper("Set the maximum homopolymer length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-max-homo-size-dist",
                    value=50,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal microsatellite size for distribution analysis", size="sm", fw=500),
                            helper("Set the minimum microsatellite length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-min-microsat-size-dist",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Maximal microsatellite size for distribution analysis", size="sm", fw=500),
                            helper("Set the maximum microsatellite length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-max-microsat-size-dist",
                    value=40,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Span size around window", size="sm", fw=500),
                            helper("Set the window size around each site for read extraction."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-span-size-window",
                    value=500,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Threads", size="sm", fw=500),
                            helper("Specify the number of threads to use for the analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Homopolymer only", size="sm", fw=500),
                            helper("Limit the output to homopolymer sites only."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-homopolymer-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Microsatellite only", size="sm", fw=500),
                            helper("Limit the output to microsatellite sites only."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-microsatellite-only",
                    checked=False,
                ),
                dmc.Switch(
                    label=dmc.Group(
                        [
                            dmc.Text("Include sites with no read coverage", size="sm", fw=500),
                            helper("Include sites with no read coverage in the output ."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-pro-pro-include-zero-coverage-sites",
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
                label="Choose a command",
                id="msisensor-pro-command-select",
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
                        "View original tool on GitHub",
                        href="https://github.com/xjtu-omics/msisensor-pro",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_select,
            html.Div(id="msisensor-pro-command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("msisensor-pro-command-container", "children"), 
    Input("msisensor-pro-command-select", "value"),
)
def msisensor_pro_select_command(value):
    if value == "scan":
        return make_scan()
    elif value == "msi":
        return make_msi()
    elif value == "pro":
        return make_pro()
    else:
        return None
    
@callback(
    Output("msisensor-pro-scan-start-button", "disabled"),
    Input("msisensor-pro-scan-refgenome-file-select", "value"),
)
def msisensor_pro_scan_start_button(refgenome):
    return not bool(refgenome)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor-pro-scan-start-button", "n_clicks"),
    State("msisensor-pro-command-select", "value"),
    State("msisensor-pro-scan-refgenome-file-select", "value"),
    State("msisensor-pro-scan-min-homo-size", "value"),
    State("msisensor-pro-scan-max-homo-size", "value"),
    State("msisensor-pro-scan-context-length", "value"),
    State("msisensor-pro-scan-max-microsat-len", "value"),
    State("msisensor-pro-scan-min-microsat-rep", "value"),
    State("msisensor-pro-scan-homopolymer-only", "checked"),
    prevent_initial_call=True,
)
def msisensor_pro_scan_start_job(
    n_clicks,
    command_key,
    reference_genome,
    min_homo_size,
    max_homo_size,
    context_len,
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
            output=f"{os.path.splitext(os.path.basename(reference_genome))[0]}.pro.microsatellite.list",
            min_homo_size=min_homo_size,
            max_homo_size=max_homo_size,
            context_len=context_len,
            max_microsat_len=max_microsat_len,
            min_microsat_rep=min_microsat_rep,
            homopolymer_only=int(bool(homopolymer_only)),
        )

        return [dict(
            title="Job started",
            action="show",
            color="yellow",
            message=f"{tool.name} scan started",
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
    Output("msisensor-pro-msi-start-button", "disabled"),
    Input("msisensor-pro-msi-microsat-list-file-select", "value"),
    Input("msisensor-pro-msi-normal-bam-file-select", "value"),
    Input("msisensor-pro-msi-tumor-bam-file-select", "value"),
)
def msisensor_pro_msi_start_button(microsatellite_list, normal_bam, tumor_bam):
    return not all([microsatellite_list, normal_bam, tumor_bam])

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor-pro-msi-start-button", "n_clicks"),
    State("msisensor-pro-command-select", "value"),
    State("msisensor-pro-msi-microsat-list-file-select", "value"),
    State("msisensor-pro-msi-normal-bam-file-select", "value"),
    State("msisensor-pro-msi-tumor-bam-file-select", "value"),

    # State("msisensor-pro-msi-refgenome-file-select", "value"),
    State("msisensor-pro-msi-coverage", "value"),
    State("msisensor-pro-msi-coverage-normalization", "checked"),
    State("msisensor-pro-msi-fdr-threshold", "value"),
    State("msisensor-pro-msi-min-homo-size-dist", "value"),
    State("msisensor-pro-msi-max-homo-size-dist", "value"),
    State("msisensor-pro-msi-min-microsat-size-dist", "value"),
    State("msisensor-pro-msi-max-microsat-size-dist", "value"),
    State("msisensor-pro-msi-span-size-window", "value"),
    State("msisensor-pro-msi-threads", "value"),
    State("msisensor-pro-msi-homopolymer-only", "checked"),
    State("msisensor-pro-msi-microsatellite-only", "checked"),
    State("msisensor-pro-msi-include-zero-coverage-sites", "checked"),
    prevent_initial_call=True,
)
def msisensor_pro_msi_start_job(
    n_clicks,
    command_key,
    microsatellite_list,
    normal_bam,
    tumor_bam,

    # reference_genome,
    coverage,
    coverage_normalization,
    fdr_threshold,
    min_homo_size_dist,
    max_homo_size_dist,
    min_microsat_size_dist,
    max_microsat_size_dist,
    span_size_window,
    threads,
    homopolymer_only,
    microsatellite_only,
    include_zero_coverage_sites,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            microsatellite_list=microsatellite_list,
            normal_bam=normal_bam,
            tumor_bam=tumor_bam,
            output=os.path.splitext(os.path.basename(tumor_bam))[0],
            
            # reference_genome=reference_genome or None,
            fdr_threshold=fdr_threshold,
            coverage=coverage,
            coverage_normalization=int(bool(coverage_normalization)),
            min_homo_size_dist=min_homo_size_dist,
            max_homo_size_dist=max_homo_size_dist,
            min_microsat_size_dist=min_microsat_size_dist,
            max_microsat_size_dist=max_microsat_size_dist,
            span_size_window=span_size_window,
            threads=threads,
            homopolymer_only=int(bool(homopolymer_only)),
            microsatellite_only=int(bool(microsatellite_only)),
            include_zero_coverage_sites=int(bool(include_zero_coverage_sites)),
        )

        return [dict(
            title="Job started",
            action="show",
            color="yellow",
            message=f"{tool.name} msi started",
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
    Output("msisensor-pro-pro-start-button", "disabled"),
    Input("msisensor-pro-pro-microsat-list-file-select", "value"),
    Input("msisensor-pro-pro-tumor-bam-file-select", "value"),
)
def msisensor_pro_pro_start_button(microsatellite_list, tumor_bam):
    return not all([microsatellite_list, tumor_bam])

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor-pro-pro-start-button", "n_clicks"),
    State("msisensor-pro-command-select", "value"),
    State("msisensor-pro-pro-microsat-list-file-select", "value"),
    State("msisensor-pro-pro-tumor-bam-file-select", "value"),

    # State("msisensor-pro-msi-refgenome-file-select", "value"),
    State("msisensor-pro-pro-instable-sites-threshold", "value"),
    State("msisensor-pro-pro-coverage", "value"),
    State("msisensor-pro-pro-min-homo-size-dist", "value"),
    State("msisensor-pro-pro-max-homo-size-dist", "value"),
    State("msisensor-pro-pro-min-microsat-size-dist", "value"),
    State("msisensor-pro-pro-max-microsat-size-dist", "value"),
    State("msisensor-pro-pro-span-size-window", "value"),
    State("msisensor-pro-pro-threads", "value"),
    State("msisensor-pro-pro-homopolymer-only", "checked"),
    State("msisensor-pro-pro-microsatellite-only", "checked"),
    State("msisensor-pro-pro-include-zero-coverage-sites", "checked"),
    prevent_initial_call=True,
)
def msisensor_pro_pro_start_job(
    n_clicks,
    command_key,
    microsatellite_list,
    tumor_bam,

    # reference_genome,
    instable_sites_threshold,
    coverage,
    min_homo_size_dist,
    max_homo_size_dist,
    min_microsat_size_dist,
    max_microsat_size_dist,
    span_size_window,
    threads,
    homopolymer_only,
    microsatellite_only,
    include_zero_coverage_sites,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            microsatellite_list=microsatellite_list,
            tumor_bam=tumor_bam,
            output=os.path.splitext(os.path.basename(tumor_bam))[0],
            
            # reference_genome=reference_genome or None,
            instable_sites_threshold=instable_sites_threshold,
            coverage=coverage,
            min_homo_size_dist=min_homo_size_dist,
            max_homo_size_dist=max_homo_size_dist,
            min_microsat_size_dist=min_microsat_size_dist,
            max_microsat_size_dist=max_microsat_size_dist,
            span_size_window=span_size_window,
            threads=threads,
            homopolymer_only=int(bool(homopolymer_only)),
            microsatellite_only=int(bool(microsatellite_only)),
            include_zero_coverage_sites=int(bool(include_zero_coverage_sites)),
        )

        return [dict(
            title="Job started",
            action="show",
            color="yellow",
            message=f"{tool.name} msi started",
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
