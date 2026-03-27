from dash import Input, Output, State, callback, no_update, html
from dash_iconify import DashIconify

from components.helper import helper
from services.job_manager import create_job
from services.file_manager import get_files

from configs.tools import TOOLS
from configs.paths import data_path

import os
import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/samtools")

tool = TOOLS["samtools"]

def make_index():
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
                            dmc.Text("BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the BAM file to index."),
                        ],
                        gap=6,
                    ),
                    id="samtools-index-bam-file-select",
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

                dmc.Button("Start", id="samtools-index-start-button", disabled=True),
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
                            helper("Specify the number of threads to use for indexing."),
                        ],
                        gap=6,
                    ),
                    id="samtools-index-threads",
                    value=1,
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

def make_merge():
    required_options = dmc.Paper(
        withBorder=True,
        radius="md",
        p="md",
        h="100%",
        children=dmc.Stack(
            [
                dmc.Title("Required options", order=4),
                dmc.MultiSelect(
                    label=dmc.Group(
                        [
                            dmc.Text("BAM files", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the BAM files to merge."),
                        ],
                        gap=6,
                    ),
                    id="samtools-merge-bam-files-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select BAM files",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="samtools-merge-start-button", disabled=True),
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
                            helper("Specify the number of threads to use for sorting."),
                        ],
                        gap=6,
                    ),
                    id="samtools-merge-threads",
                    value=1,
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

def make_sort():
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
                            dmc.Text("BAM file", size="sm", fw=500),
                            dmc.Text("*", c="red", size="sm", fw=700),
                            helper("Select the BAM file to sort."),
                        ],
                        gap=6,
                    ),
                    id="samtools-sort-bam-file-select",
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

                dmc.Button("Start", id="samtools-sort-start-button", disabled=True),
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
                            helper("Specify the number of threads to use for sorting."),
                        ],
                        gap=6,
                    ),
                    id="samtools-sort-threads",
                    value=1,
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

def make_faidx():
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
                    id="samtools-faidx-refgenome-file-select",
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

                dmc.Button("Start", id="samtools-faidx-start-button", disabled=True),
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
                            helper("Specify the number of threads to use for indexing."),
                        ],
                        gap=6,
                    ),
                    id="samtools-faidx-threads",
                    value=1,
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
                id="samtools-command-select",
                value="index",
                data=[
                    {"value": command.key, "label": command.name}
                    for command in tool.commands.values()
                ],
                allowDeselect=False,
            ),
            dmc.Text(id="samtools-command-description"),
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
                        href="https://github.com/samtools/samtools",
                        target="_blank",
                    ),
                    dmc.Text("|"),
                    DashIconify(icon="bi:globe", width=18),
                    dmc.Anchor(
                        "Official website",
                        href="https://www.htslib.org/",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_select,
            html.Div(id="samtools-command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("samtools-command-container", "children"), 
    Input("samtools-command-select", "value"),
)
def samtools_select_command(value):
    if value == "index":
        return make_index()
    elif value == "merge":
        return make_merge()
    elif value == "sort":
        return make_sort()
    elif value == "faidx":
        return make_faidx()
    else:
        return None
    
@callback(
    Output("samtools-index-start-button", "disabled"),
    Input("samtools-index-bam-file-select", "value"),
)
def samtools_index_start_button(bam_file):
    return not bool(bam_file)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("samtools-index-start-button", "n_clicks"),
    State("samtools-command-select", "value"),
    State("samtools-index-bam-file-select", "value"),
    State("samtools-index-threads", "value"),
    prevent_initial_call=True,
)
def samtools_index_start_job(
    n_clicks,
    command_key,
    bam_file,
    threads,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            bam_file=bam_file,
            output=f"{os.path.basename(bam_file)}.bai",

            threads=(threads-1) if threads > 1 else None,
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
    Output("samtools-sort-start-button", "disabled"),
    Input("samtools-sort-bam-file-select", "value"),
)
def samtools_sort_start_button(bam_file):
    return not bool(bam_file)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("samtools-sort-start-button", "n_clicks"),
    State("samtools-command-select", "value"),
    State("samtools-sort-bam-file-select", "value"),
    State("samtools-sort-threads", "value"),
    prevent_initial_call=True,
)
def samtools_sort_start_job(
    n_clicks,
    command_key,
    bam_file,
    threads,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            bam_file=bam_file,
            output=f"{os.path.splitext(os.path.basename(bam_file))[0]}.sorted.bam",

            threads=(threads-1) if threads > 1 else None,
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
    Output("samtools-merge-start-button", "disabled"),
    Input("samtools-merge-bam-files-select", "value"),
)
def samtools_merge_start_button(bam_files):
    if bam_files and len(bam_files) > 1:
        return False
    return True

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("samtools-merge-start-button", "n_clicks"),
    State("samtools-command-select", "value"),
    State("samtools-merge-bam-files-select", "value"),
    State("samtools-merge-threads", "value"),
    prevent_initial_call=True,
)
def samtools_merge_start_job(
    n_clicks,
    command_key,
    bam_files,
    threads,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            bam_files=" ".join(bam_files),
            output=f"{os.path.splitext(os.path.basename(bam_files[0]))[0]}.merged.bam",

            threads=(threads-1) if threads > 1 else None,

            save_next_to=bam_files[0],
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
    Output("samtools-faidx-start-button", "disabled"),
    Input("samtools-faidx-refgenome-file-select", "value"),
)
def samtools_faidx_start_button(reference_genome):
    return not bool(reference_genome)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("samtools-faidx-start-button", "n_clicks"),
    State("samtools-command-select", "value"),
    State("samtools-faidx-refgenome-file-select", "value"),
    State("samtools-faidx-threads", "value"),
    prevent_initial_call=True,
)
def samtools_faidx_start_job(
    n_clicks,
    command_key,
    reference_genome,
    threads,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get(command_key),
            reference_genome=reference_genome,
            output=f"{os.path.basename(reference_genome)}.fai",

            threads=(threads-1) if threads > 1 else None,
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
    Output("samtools-command-description", "children"),
    Input("samtools-command-select", "value"),
)
def msisensor_command_description(command_key):
    command = tool.commands.get(command_key)
    return command.description if command else "No description available."