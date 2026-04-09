import dash_mantine_components as dmc

from dash_iconify import DashIconify

def helper(help_message: str):
    """
    returns a small hover tooltip with a help message for user
    """
    return dmc.HoverCard(
        withArrow=True,
        width=260,
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
                dmc.Text(
                    help_message,
                    size="sm",
                    style={"whiteSpace": "normal"},
                )
            ),
        ],
    )