import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html, dcc

def loading_block(children):
    return dcc.Loading(
        type="circle",
        delay_show=150,
        overlay_style={"visibility":"visible", "filter": "blur(2px)"},
        children=html.Div(children)
    )

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
                loading_block(
                    dmc.Box(children=children, pt="xs")
                )
            ),
        ],
    )