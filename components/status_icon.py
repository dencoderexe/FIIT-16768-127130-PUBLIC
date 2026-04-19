from dash_iconify import DashIconify

from models.jobs import Status

import dash_mantine_components as dmc

def status_icon(status: Status):
    return dmc.ThemeIcon(
        DashIconify(icon=status.icon, height=22),
        color=status.color,
        variant="light",
        radius="xl",
        size="md",
    )
