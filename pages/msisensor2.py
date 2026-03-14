import dash
import dash_mantine_components as dmc

from dash import Input, Output, State, callback, dcc, html, no_update, ALL, ctx
from dash_iconify import DashIconify

from services.job_manager import TOOLS
from services.file_manager import get_files, get_dirs

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
                    label="Model",
                    id="model-select",
                    data=[
                        {"value": "models_b37_HumanG1Kv37", "label": "b37 (HumanG1Kv37)"},
                        {"value": "models_hg19_GRCh37", "label": "hg19 / GRCh37"},
                        {"value": "models_hg38", "label": "hg38 / GRCh38"},
                    ],
                    withAsterisk=True,
                    allowDeselect=False,
                    checkIconPosition="right",
                    placeholder="Select model",
                ),
                dmc.Select(
                    label="Tumor .BAM file",
                    id="bam-file-select",
                    data=[
                        {"value": str(file), "label": str(file)}
                        for file in get_files(extensions=[".bam"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select .BAM file",
                    searchable=True,
                    withAsterisk=True,
                ),
                dmc.Space(h="xl"),
                dmc.Button("Start", id="start-button"),
            ],
            gap="md",
            justify="space-between",
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
                    label="Coverage",
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
                    label="Threads",
                    id="threads",
                    value=1,
                    min=1,
                    allowDecimal=False,
                ),
                dmc.Switch(
                    label="Homopolymer only",
                    id="homopolymer-only",
                    checked=False,
                ),
                dmc.Switch(
                    label="Microsatellite only",
                    id="microsatellite-only",
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
                id="command-select",
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
            html.Div(id="command-container"),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)

@callback(
    Output("command-container", "children"), 
    Input("command-select", "value"),
)
def select_command(value):
    if value == "msi":
        return make_msi()
    else:
        return None