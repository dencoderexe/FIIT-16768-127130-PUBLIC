import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/")

layout = dmc.Container(
    [
        # dmc.Title("MSI Analyzer", order=1),
        # dmc.Space(h="md"),
        dmc.Text("Welcome to the home page."),
    ],
    fluid=True,
    p="md",
)