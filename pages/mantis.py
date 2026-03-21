from dash import Input, Output, State, callback, html, no_update
from dash_iconify import DashIconify

from components.helper import helper
from services.job_manager import create_job
from services.file_manager import get_files

from configs.tools import TOOLS
from configs.paths import data_path

import os
import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/mantis")

tool = TOOLS["mantis"]

def make_mantis():
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
                            dmc.Text("Normal BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Normal BAM file"),
                        ],
                        gap=6,
                    ),
                    id="mantis-normal-bam-file-select",
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
                            helper("Tumor BAM file"),
                        ],
                        gap=6,
                    ),
                    id="mantis-tumor-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select tumor BAM file",
                    searchable=True,
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("Reference genome file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Reference genome sequences file in .fasta format"),
                        ],
                        gap=6,
                    ),
                    id="mantis-refgenome-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".fasta", ".fas", ".fa", ".fna", ".ffn", ".faa", ".mpfa", ".frn"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select reference genome FASTA file",
                    searchable=True,
                ),
                dmc.Select(
                    label=dmc.Group(
                        [
                            dmc.Text("BED file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("BED file"),
                        ],
                        gap=6,
                    ),
                    id="mantis-bed-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bed"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select BED file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="mantis-start-button", disabled=True),
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
                            dmc.Text("Threads", size="sm", fw=500),
                            helper("Threads number for parallel computing"),
                        ],
                        gap=6,
                    ),
                    id="mantis-threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum read quality", size="sm", fw=500),
                            helper(("Minimum average per-base read quality for a read to pass the quality control filters. "
                                   "Default: 25.0")),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-read-quality",
                    value=25.0,
                    min=0,
                    step=0.1,
                    decimalScale=1,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum locus quality", size="sm", fw=500),
                            helper(("Minimum average per-base quality for the bases contained within the microsatellite locus. "
                                    "Reads that pass the read quality filter (above) will still fail quality control if the locus "
                                    "quality scores are too low. Default: 30.0")),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-locus-quality",
                    value=30.0,
                    min=0,
                    step=0.1,
                    decimalScale=1,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum read length", size="sm", fw=500),
                            helper(("Minimum read length for a read to pass quality control. Only bases that are not clipped will "
                                    "be considered; in other words, soft-clipped or hard-clipped parts of the read do not count "
                                    "towards the length. Default: 35")),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-read-length",
                    value=35,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum locus coverage", size="sm", fw=500),
                            helper(("Minimum coverage (after QC filters) required for each of the normal and tumor samples for a "
                                    "locus to be considered in the calculations. Default: 30")),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-locus-coverage",
                    value=30,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum repeat reads", size="sm", fw=500),
                            helper(("Minimum reads supporting a specific repeat count. Repeat counts that have less than this value "
                                    "will be discarded as part of outlier filtering. Default: 3")),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-repeat-reads",
                    value=3,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Standard deviations", size="sm", fw=500),
                            helper(("Standard deviations from the mean before a repeat count is considered an outlier and discarded. "
                                    "Default: 3.0")),
                        ],
                        gap=6,
                    ),
                    id="mantis-standard-deviations",
                    value=3.0,
                    min=0,
                    step=0.1,
                    decimalScale=1,
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
                id="mantis-command-select",
                value="mantis",
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
                        href="https://github.com/OSU-SRLab/MANTIS",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_select,
            html.Div(id="mantis-command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("mantis-command-container", "children"), 
    Input("mantis-command-select", "value"),
)
def select_command(value):
    if value == "mantis":
        return make_mantis()
    else:
        return None
    
@callback(
    Output("mantis-start-button", "disabled"),
    Input("mantis-normal-bam-file-select", "value"),
    Input("mantis-tumor-bam-file-select", "value"),
    Input("mantis-refgenome-file-select", "value"),
    Input("mantis-bed-file-select", "value"),
)
def mantis_start_button(normal_bam, tumor_bam, refgenome, bed_file):
    return not all([normal_bam, tumor_bam, refgenome, bed_file])

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("mantis-start-button", "n_clicks"),
    State("mantis-command-select", "value"),
    State("mantis-normal-bam-file-select", "value"),
    State("mantis-tumor-bam-file-select", "value"),
    State("mantis-refgenome-file-select", "value"),
    State("mantis-bed-file-select", "value"),
    State("mantis-threads", "value"),
    State("mantis-min-read-quality", "value"),
    State("mantis-min-locus-quality", "value"),
    State("mantis-min-read-length", "value"),
    State("mantis-min-locus-coverage", "value"),
    State("mantis-min-repeat-reads", "value"),
    State("mantis-standard-deviations", "value"),
    prevent_initial_call=True,
)
def mantis_start_job(
    n_clicks,
    command_key,
    normal_bam,
    tumor_bam,
    reference_genome,
    bed_file,
    threads,
    min_read_quality,
    min_locus_quality,
    min_read_length,
    min_locus_coverage,
    min_repeat_reads,
    standard_deviations,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            normal_bam=normal_bam,
            tumor_bam=tumor_bam,
            reference_genome=reference_genome,
            bed_file=bed_file,
            output=os.path.splitext(os.path.basename(tumor_bam))[0],

            threads=threads,
            min_read_quality=min_read_quality,
            min_locus_quality=min_locus_quality,
            min_read_length=min_read_length,
            min_locus_coverage=min_locus_coverage,
            min_repeat_reads=min_repeat_reads,
            standard_deviations=standard_deviations,
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