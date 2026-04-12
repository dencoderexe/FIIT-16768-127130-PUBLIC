import dash_mantine_components as dmc

from models.jobs import Job
from components.job_arg_table import job_arg_table

from dash_iconify import DashIconify

def helper(content: str|Job):
    """
    Returns a small hover tooltip with a help message for user.
    """
    return dmc.HoverCard(
        withArrow=True,
        shadow="xs",
        position="top",
        openDelay=150,
        children=[
            dmc.HoverCardTarget(
                dmc.ActionIcon(
                    DashIconify(icon="bi:question-circle", width=13),
                    variant="subtle",
                    size="xs",
                )
            ),
            dmc.HoverCardDropdown(
                style={
                    "maxHeight": "400px",
                    "overflowY": "auto",
                    "maxWidth": "600px",
                },
                children=(
                    dmc.Text(
                        content,
                        size="sm",
                        style={"whiteSpace": "pre-line"},
                    )
                    if isinstance(content, str)
                    else dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Text("Run parameters", size="sm", fw=500),
                            job_arg_table(content),
                        ],
                    )
                )
            ),
        ],
    )
