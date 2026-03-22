from dash import Input, Output, State, callback, html, no_update
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
                            helper("Select the reference genome file in FASTA format."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-scan-refgenome-file-select",
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
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal homopolymer size", size="sm", fw=500),
                            helper("Set the minimum homopolymer length to include in the scan."),
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
                            helper("Set the maximum homopolymer length to include in the scan."),
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
                            helper("Set the number of flanking bases to include as sequence context."),
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
                            helper("Set the maximum microsatellite motif length to include in the scan."),
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
                            dmc.Text("Minimal repeat times of microsatellite", size="sm", fw=500),
                            helper("Set the minimum number of repeat units required for a microsatellite to be included."),
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
                            helper("Limit the output to homopolymer sites only."),
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
                    id="msisensor-msi-microsat-list-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".microsatellite.list"])
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
                    id="msisensor-msi-normal-bam-file-select",
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
                    id="msisensor-msi-tumor-bam-file-select",
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

                dmc.Button("Start", id="msisensor-msi-start-button", disabled=True),
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
                            dmc.Text("BED file", size="sm", fw=500),
                            helper("Select an optional BED file defining genomic regions for analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-bed-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bed"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select BED file",
                    searchable=True,
                ),
                dmc.TextInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Region", size="sm", fw=500),
                            helper("Specify an optional genomic region in the format chr:start-end."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-region",
                    placeholder="e.g. 1:10000000-20000000",
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Coverage", size="sm", fw=500),
                            helper("Select the recommended coverage threshold for the input data type."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-coverage",
                    value="20",
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
                    id="msisensor-msi-coverage-normalization",
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
                    id="msisensor-msi-fdr-threshold",
                    value=0.05,
                    min=0,
                    step=0.01,
                    decimalScale=2,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal homopolymer size", size="sm", fw=500),
                            helper("Set the minimum homopolymer length to include in the analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-min-homo-size",
                    value=5,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal homopolymer size for distribution analysis", size="sm", fw=500),
                            helper("Set the minimum homopolymer length to use for distribution analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-min-homo-size-dist",
                    value=10,
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
                    id="msisensor-msi-max-homo-size-dist",
                    value=50,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimal microsatellite size", size="sm", fw=500),
                            helper("Set the minimum microsatellite length to include in the analysis."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-min-microsat-size",
                    value=3,
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
                    id="msisensor-msi-min-microsat-size-dist",
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
                    id="msisensor-msi-max-microsat-size-dist",
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
                    id="msisensor-msi-span-size-window",
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
                    id="msisensor-msi-threads",
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
                    id="msisensor-msi-homopolymer-only",
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
                    id="msisensor-msi-microsatellite-only",
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
                        "View original tool on GitHub",
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
def samtools_select_command(value):
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
            output=f"{os.path.splitext(os.path.basename(reference_genome))[0]}.microsatellite.list",
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
    Output("msisensor-msi-start-button", "disabled"),
    Input("msisensor-msi-microsat-list-file-select", "value"),
    Input("msisensor-msi-normal-bam-file-select", "value"),
    Input("msisensor-msi-tumor-bam-file-select", "value"),
    Input("msisensor-msi-region", "value"),
)
def msisensor_msi_start_button(microsatellite_list, normal_bam, tumor_bam, region):
    if not all([microsatellite_list, normal_bam, tumor_bam]):
        return True

    if region:
        valid, error = validate_region(region)
        return not valid

    return False

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("msisensor-msi-start-button", "n_clicks"),
    State("msisensor-command-select", "value"),
    State("msisensor-msi-microsat-list-file-select", "value"),
    State("msisensor-msi-normal-bam-file-select", "value"),
    State("msisensor-msi-tumor-bam-file-select", "value"),
    State("msisensor-msi-bed-file-select", "value"),
    State("msisensor-msi-region", "value"),
    State("msisensor-msi-coverage", "value"),
    State("msisensor-msi-coverage-normalization", "checked"),
    State("msisensor-msi-fdr-threshold", "value"),
    State("msisensor-msi-min-homo-size", "value"),
    State("msisensor-msi-min-homo-size-dist", "value"),
    State("msisensor-msi-max-homo-size-dist", "value"),
    State("msisensor-msi-min-microsat-size", "value"),
    State("msisensor-msi-min-microsat-size-dist", "value"),
    State("msisensor-msi-max-microsat-size-dist", "value"),
    State("msisensor-msi-span-size-window", "value"),
    State("msisensor-msi-threads", "value"),
    State("msisensor-msi-homopolymer-only", "checked"),
    State("msisensor-msi-microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def msisensor_msi_start_job(
    n_clicks,
    command_key,
    microsatellite_list,
    normal_bam,
    tumor_bam,
    bed_file,
    region,
    coverage,
    coverage_normalization,
    fdr_threshold,
    min_homo_size,
    min_homo_size_dist,
    max_homo_size_dist,
    min_microsat_size,
    min_microsat_size_dist,
    max_microsat_size_dist,
    span_size_window,
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
            microsatellite_list=microsatellite_list,
            normal_bam=normal_bam,
            tumor_bam=tumor_bam,
            output=os.path.splitext(os.path.basename(tumor_bam))[0],
            
            bed_file=bed_file or None,
            region=region or None,
            fdr_threshold=fdr_threshold,
            coverage=coverage,
            coverage_normalization=int(bool(coverage_normalization)),
            min_homo_size=min_homo_size,
            min_homo_size_dist=min_homo_size_dist,
            max_homo_size_dist=max_homo_size_dist,
            min_microsat_size=min_microsat_size,
            min_microsat_size_dist=min_microsat_size_dist,
            max_microsat_size_dist=max_microsat_size_dist,
            span_size_window=span_size_window,
            threads=threads,
            homopolymer_only=int(bool(homopolymer_only)),
            microsatellite_only=int(bool(microsatellite_only)),
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
    Output("msisensor-msi-region", "error"),
    Input("msisensor-msi-region", "value"),
)
def validate_region_input(region):
    if not region:
        return None

    valid, error = validate_region(region)

    return error

def validate_region(region: str):
    if not region:
        return True, None

    m = re.fullmatch(r"([^:\s]+):(\d+)-(\d+)", region.strip())
    if not m:
        return False, "Format: chr:start-end"

    if int(m.group(2)) >= int(m.group(3)):
        return False, "Start must be < End"

    return True, None