import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify

dash.register_page(__name__)

layout = dmc.Center(
    style={"height": "50vh"},
    children = [
        dmc.Title([
            "404 Page Not Found ", DashIconify(icon='bi:emoji-frown-fill', height=35)
        ])
    ]
)