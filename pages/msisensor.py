from dash import Input, Output, State, callback, html, no_update, ctx
from dash_iconify import DashIconify

from components.helper import helper
from services.job_manager import create_job
from services.file_manager import get_files

from configs.tools import TOOLS
from configs.paths import data_path, BAM_EXT, BED_EXT, FASTA_EXT, MICROSAT_LIST_EXT

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
                        for file in get_files(extensions=FASTA_EXT)
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
                            dmc.Text("Minimum homopolymer size", size="sm", fw=500),
                            helper(
                                "Minimum homopolymer length to include in the scan.\n"
                                "Example: with value 5, homopolymers shorter than 5 bases will be ignored."
                            ),
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
                            dmc.Text("Maximum homopolymer size", size="sm", fw=500),
                            helper(
                                "Maximum homopolymer length to include in the scan.\n"
                                "Example: with value 50, homopolymers longer than 50 bases will be ignored."
                            ),
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
                            helper(
                                "Number of flanking bases to store on each side of the detected locus."
                            ),
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
                            dmc.Text("Maximum microsatellite motif length", size="sm", fw=500),
                            helper(
                                "Maximum repeat unit length to consider when scanning microsatellite loci.\n"
                                "Example: with value 5, motifs longer than 5 bases will be ignored."
                            ),
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
                            dmc.Text("Minimum microsatellite repeats", size="sm", fw=500),
                            helper(
                                "Minimum number of repeat units required for a microsatellite to be reported.\n"
                                "Example: with value 3, (AC)2 will be ignored."
                            ),
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
                            helper(
                                "Restrict the output to homopolymer loci only."
                            ),
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
                            helper("Select the microsatellite list file generated by the scan command."),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-microsat-list-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=MICROSAT_LIST_EXT)
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
                    id="msisensor-msi-tumor-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=BAM_EXT)
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
                            dmc.Text("Normal BAM file", size="sm", fw=500),
                            helper(
                                "Optional BAM file for the matched normal sample. Provide this to run tumor-normal analysis."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-normal-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=BAM_EXT)
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select normal BAM file",
                    searchable=True,
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("BED file", size="sm", fw=500),
                            helper(
                                "Optional BED file defining genomic regions or loci to include in the analysis."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-bed-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=BED_EXT)
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
                            helper(
                                "Optional genomic region in the format chr:start-end.\n"
                                "Example: 1:10000000-20000000."
                            ),
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
                            helper(
                                "Minimum sequencing depth threshold used for analysis.\n"
                                "Recommended defaults are 20 for WXS and 15 for WGS."
                            ),
                        ],
                        gap=6,
                    ),
                    id="msisensor-msi-coverage",
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
                            helper(
                                "Enable coverage normalization for paired tumor-normal analysis."
                            ),
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
                            helper(
                                "False discovery rate threshold used for calling unstable sites."
                            ),
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
                            dmc.Text("Minimum homopolymer size", size="sm", fw=500),
                            helper(
                                "Minimum homopolymer length to include in MSI analysis."
                            ),
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
                            dmc.Text("Minimum homopolymer size for distribution analysis", size="sm", fw=500),
                            helper(
                                "Minimum homopolymer length to include when computing repeat length distributions."
                            ),
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
                            dmc.Text("Maximum homopolymer size for distribution analysis", size="sm", fw=500),
                            helper(
                                "Maximum homopolymer length to include when computing repeat length distributions."
                            ),
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
                            dmc.Text("Minimum microsatellite motif length", size="sm", fw=500),
                            helper(
                                "Minimum microsatellite repeat unit length to include in MSI analysis."
                            ),
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
                            dmc.Text("Minimum microsatellite motif length for distribution analysis", size="sm", fw=500),
                            helper(
                                "Minimum microsatellite repeat unit length to include when computing repeat length distributions."
                            ),
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
                            dmc.Text("Maximum microsatellite motif length for distribution analysis", size="sm", fw=500),
                            helper(
                                "Maximum microsatellite repeat unit length to include when computing repeat length distributions."
                            ),
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
                            dmc.Text("Span size window", size="sm", fw=500),
                            helper(
                                "Window size around each locus used for read extraction."
                            ),
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
                            helper(
                                "Number of threads to use for analysis."
                            ),
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
                            helper(
                                "Restrict the analysis to homopolymer loci only."
                            ),
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
                            helper(
                                "Restrict the analysis to microsatellite loci only."
                            ),
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
            dmc.Text(
                id="msisensor-command-description",
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
def msisensor_select_command(value):
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
            output=f"{os.path.splitext(os.path.basename(reference_genome))[0]}{MICROSAT_LIST_EXT[0]}",
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
    Input("msisensor-msi-tumor-bam-file-select", "value"),
    Input("msisensor-msi-region", "value"),
)
def msisensor_msi_start_button(microsatellite_list, tumor_bam, region):
    if not all([microsatellite_list, tumor_bam]):
        return True

    if region:
        valid, _ = validate_region(region)
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
            normal_bam=normal_bam or None,
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
    Output("msisensor-msi-homopolymer-only", "checked"),
    Output("msisensor-msi-microsatellite-only", "checked"),
    Input("msisensor-msi-homopolymer-only", "checked"),
    Input("msisensor-msi-microsatellite-only", "checked"),
    prevent_initial_call=True,
)
def msisensor_msi_homopolymer_microsatellite_only_switch(homopolymer_only, microsatellite_only):
    triggered = ctx.triggered_id

    if triggered == "msisensor-msi-homopolymer-only" and homopolymer_only:
        return True, False

    if triggered == "msisensor-msi-microsatellite-only" and microsatellite_only:
        return False, True

    return homopolymer_only, microsatellite_only
    
@callback(
    Output("msisensor-msi-region", "error"),
    Input("msisensor-msi-region", "value"),
)
def msisensor_validate_region_input(region):
    if not region:
        return None

    _, error = validate_region(region)

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

@callback(
    Output("msisensor-command-description", "children"),
    Input("msisensor-command-select", "value"),
)
def msisensor_command_description(command_key):
    command = tool.commands.get(command_key)
    return command.description if command else "No description available."