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

dash.register_page(__name__, path="/microsat2bed")

tool = TOOLS["microsat2bed"]

def make_convert():
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
                    id="microsat2bed-convert-microsat-list-file-select",
                    data=[
                        {"value": str(file), "label": str(file).replace(data_path, "")}
                        for file in get_files(extensions=[".microsatellite.list"])
                    ],
                    nothingFoundMessage="Nothing found",
                    checkIconPosition="right",
                    placeholder="Select microsatellite list file",
                    searchable=True,
                ),
                dmc.Space(h="xl"),
                
                dmc.Box(style={"flexGrow": 1}),

                dmc.Button("Start", id="microsat2bed-convert-start-button", disabled=True),
            ],
            gap="md",
            h="100%",
        ),
    )

    return dmc.Grid(
        [
            dmc.GridCol(required_options, span=12),
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
            dmc.Text(tool.commands["convert"].description),
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
                        "Tool source code on GitHub",
                        href="https://github.com/dencoderexe/",
                        target="_blank",
                    ),
                ],
                gap="xs",
            ),
            command_description,
            make_convert(),
        ],
        gap="md",
    ),
    fluid=True,
    p="md",
)
    
@callback(
    Output("microsat2bed-convert-start-button", "disabled"),
    Input("microsat2bed-convert-microsat-list-file-select", "value"),
)
def microsat2bed_convert_start_button(microsatellite_list):
    return not bool(microsatellite_list)

@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("microsat2bed-convert-start-button", "n_clicks"),
    Input("microsat2bed-convert-microsat-list-file-select", "value"),
    prevent_initial_call=True,
)
def microsat2bed_convert_start_job(
    n_clicks,
    microsatellite_list,
):
    if not n_clicks:
        return no_update

    try:
        create_job(
            tool=tool,
            command=tool.commands.get("convert"),
            microsatellite_list=microsatellite_list,
            output=f"{os.path.basename(microsatellite_list)}.bed",
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
