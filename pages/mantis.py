from dash import Input, Output, State, callback, no_update
from dash_iconify import DashIconify

from components.helper import helper
from components.notifications import job_started_notification, job_started_failed_notification
from services.job_manager import create_job
from services.file_manager import get_files, build_output_name

from configs.tools import TOOLS
from configs.paths import data_path, BAM_EXT, BED_EXT, FASTA_EXT

import os
import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/mantis")

tool = TOOLS["mantis"]

def make_mantis():
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
                            dmc.Text("Normal BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper(
                                "Select the BAM file for the matched normal sample."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-normal-bam-file-select",
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
                            dmc.Text("Tumor BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper(
                                "Select the BAM file for the tumor sample."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-tumor-bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=BAM_EXT)
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
                            helper(
                                "Select the reference genome file in FASTA format."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-refgenome-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=FASTA_EXT)
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
                            helper(
                                "Select the BED file containing the targeted MSI loci. "
                                "The BED file must follow the format expected by MANTIS."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-bed-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=BED_EXT)
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select BED file",
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
                    id="mantis-output-name-input",
                    placeholder="Leave empty to use the default file name",
                ),

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
                            helper(
                                "Number of threads to use for multiprocessing."
                            ),
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
                            helper(
                                "Minimum average per-base read quality required for a read to pass quality control.\n"
                                "Example: reads with average quality below 25.0 will be discarded."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-read-quality",
                    value=20,
                    min=0,
                    step=0.1,
                    decimalScale=1,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum locus quality", size="sm", fw=500),
                            helper(
                                "Minimum average per-base quality for bases within the microsatellite locus.\n"
                                "Reads that pass the read quality filter may still be discarded if locus quality is too low."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-locus-quality",
                    value=25,
                    min=0,
                    step=0.1,
                    decimalScale=1,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum read length", size="sm", fw=500),
                            helper(
                                "Minimum unclipped read length required for a read to pass quality control.\n"
                                "Soft-clipped and hard-clipped bases are not counted.\n"
                                "Example: with value 35, reads shorter than 35 unclipped bases will be discarded."
                            ),
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
                            helper(
                                "Minimum coverage required in both normal and tumor samples for a locus to be included in the analysis.\n"
                                "Coverage is evaluated after quality control filtering."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-locus-coverage",
                    value=15,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Minimum repeat reads", size="sm", fw=500),
                            helper(
                                "Minimum number of reads supporting a specific repeat count for that repeat count to be retained.\n"
                                "Repeat counts supported by fewer reads are discarded during outlier filtering."
                            ),
                        ],
                        gap=6,
                    ),
                    id="mantis-min-repeat-reads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.NumberInput(
                    label=dmc.Group(
                        [
                            dmc.Text("Standard deviations", size="sm", fw=500),
                            helper(
                                "Number of standard deviations from the mean allowed before a repeat count is treated as an outlier "
                                "and discarded.\n"
                                "Example: with value 3.0, repeat counts far from the mean distribution are removed."
                            ),
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
                tool.commands["mantis"].description,
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
                        href="https://github.com/OSU-SRLab/MANTIS",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_description,
            make_mantis(),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)
    
@callback(
    Output("mantis-start-button", "disabled"),
    Input("mantis-normal-bam-file-select", "value"),
    Input("mantis-tumor-bam-file-select", "value"),
    Input("mantis-refgenome-file-select", "value"),
    Input("mantis-bed-file-select", "value"),
)
def mantis_start_button(normal_bam, tumor_bam, reference_genome, bed_file):
    return not all([normal_bam, tumor_bam, reference_genome, bed_file])

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("mantis-start-button", "n_clicks"),
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
    State("mantis-output-name-input", "value"),
    prevent_initial_call=True,
)
def mantis_start_job(
    n_clicks,
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
    output_name,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get("mantis"),
            normal_bam=normal_bam,
            tumor_bam=tumor_bam,
            reference_genome=reference_genome,
            bed_file=bed_file,
            output=build_output_name(os.path.splitext(os.path.basename(tumor_bam))[0], output_name, None),

            threads=threads,
            min_read_quality=min_read_quality,
            min_locus_quality=min_locus_quality,
            min_read_length=min_read_length,
            min_locus_coverage=min_locus_coverage,
            min_repeat_reads=min_repeat_reads,
            standard_deviations=standard_deviations,
        )

        return job_started_notification(f"{tool.name} started")

    except Exception as e:
        return job_started_failed_notification(e)