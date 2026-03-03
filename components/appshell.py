from dash import Dash, html, dcc, Input, Output, State, callback, no_update, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

logo = "/assets/fiit/PNG/STU-FIIT-nvf.png"

def make_appshell(content):
    theme_toggle = dmc.Switch(
        offLabel=DashIconify(
            icon="radix-icons:sun", width=20, color= "var(--mantine-color-yellow-8)"
        ),
        onLabel=DashIconify(
            icon="radix-icons:moon",
            width=20,
            color= "var(--mantine-color-yellow-6)",
        ),
        id="color-scheme-toggle",
        persistence=True,
        color="grey",
        size="md",
    )

    return dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Burger(
                                    id="burger",
                                    size="sm",
                                    hiddenFrom="sm",
                                    opened=False,
                                ),
                                dmc.Image(src=logo, h=50, flex=0),
                                dmc.Title("MSI Analyzer", c="blue"),
                            ]
                        ),
                        theme_toggle,
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px="md",
                ),
            ),
            dmc.AppShellNavbar(
                id="navbar",
                children=[
                    "Navbar",
                    dmc.NavLink(
                        label="Tools",
                        childrenOffset=12,
                        leftSection=DashIconify(icon="bi:tools", height=16),
                        children=[
                            dmc.NavLink(label="Samtools", href="/samtools"),
                            dmc.NavLink(label="MSISensor", href="/msisensor"),
                            dmc.NavLink(label="MSISensor-2", href="/msisensor-2"),
                            dmc.NavLink(label="MSISensor-Pro", href="/msisensor-pro"),
                            dmc.NavLink(label="MANTIS", href="/mantis"),
                        ],
                    ),
                    dmc.NavLink(label="Jobs", href="/jobs", leftSection=DashIconify(icon="bi:terminal-fill", height=16)),
                    dmc.NavLink(label="Results", href="/results", leftSection=DashIconify(icon="bi:bar-chart-fill", height=16)),
                ],
                p="md",
            ),
            dmc.AppShellMain(content),
        ],
        header={"height": 60},
        padding="md",
        navbar={
            "width": 200,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        },
        id="appshell",
    )

def make_appshell_callbacks(app):
    @callback(
        Output("appshell", "navbar"),
        Input("burger", "opened"),
        State("appshell", "navbar"),
    )
    def navbar_is_open(opened, navbar):
        navbar["collapsed"] = {"mobile": not opened}
        return navbar


    clientside_callback(
        """ 
        (switchOn) => {
        document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'dark' : 'light');  
        return window.dash_clientside.no_update
        }
        """,
        Output("color-scheme-toggle", "id"),
        Input("color-scheme-toggle", "checked"),
    )