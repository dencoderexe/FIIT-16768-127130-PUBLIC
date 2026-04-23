import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html, dcc

def make_section(value: str, title: str, children, icon: str | None = None):
    return dmc.AccordionItem(
        value=value,
        children=[
            dmc.AccordionControl(
                dmc.Group(
                    gap="sm",
                    children=[
                        DashIconify(icon=icon, height=18) if icon else None,
                        dmc.Text(title, fw=700),
                    ],
                )
            ),
            dmc.AccordionPanel(
                dmc.Box(children=children, pt="xs")
            ),
        ],
    )