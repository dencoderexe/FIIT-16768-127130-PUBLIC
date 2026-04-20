import dash_mantine_components as dmc

from dash import Input, Output, State, callback, clientside_callback, html, dcc
from dash_iconify import DashIconify

# the main AppShell structure was inspired by the official Mantine example:
# https://github.com/snehilvj/dmc-docs/blob/main/help_center/appshell/appshell_with_theme_switch.py

logo = "/assets/fiit/PNG/STU-FIIT-nvf.png"

def make_appshell(content):
    # toggle between light and dark theme (client-side controlled)
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
            # dummy Div used as a target for clientside theme switching
            html.Div(id="theme-dummy", style={"display": "none"}),

            # header
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                # burger menu for collapsing navbar on small screens
                                dmc.Burger(
                                    id="burger",
                                    size="sm",
                                    hiddenFrom="sm",
                                    opened=False,
                                ),
                                # FIIT STU logo
                                html.A(
                                    dmc.Image(
                                        src=logo,
                                        h=50,
                                        flex=0,
                                        style={"cursor": "pointer"}
                                    ),
                                    href="https://www.fiit.stuba.sk/",
                                    target="_blank",
                                ),
                                dmc.Title("MSI Pipeline Dashboard", c="blue"),
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
            # sidebar navigation
            dmc.AppShellNavbar(
                id="navbar",
                children=[
                    # home page
                    dmc.NavLink(label=dmc.Text("Home", size="md"), href="/", leftSection=DashIconify(icon="bi:house-door-fill", height=16)),
                    # tool pages
                    dmc.NavLink(
                        label=dmc.Text("Tools", size="md"),
                        childrenOffset=12,
                        leftSection=DashIconify(icon="bi:tools", height=16),
                        children=[
                            dmc.Text(
                                "Data processing",
                                size="xs",
                                c="dimmed",
                                fw=700,
                                tt="uppercase",
                            ),
                            dmc.Divider(),

                            dmc.NavLink(label="Samtools", href="/samtools"),
                            dmc.NavLink(label="RepeatFinder", href="/repeatfinder"),
                            dmc.NavLink(label="MSlist Converter", href="/mslist_converter"),

                            dmc.Text(
                                "MSI analysis", 
                                size="xs", 
                                c="dimmed", 
                                fw=700, 
                                tt="uppercase"),
                            dmc.Divider(),

                            dmc.NavLink(label="MSIsensor", href="/msisensor"),
                            dmc.NavLink(label="MSIsensor2", href="/msisensor2"),
                            dmc.NavLink(label="MSIsensor-pro", href="/msisensor-pro"),
                            dmc.NavLink(label="MANTIS", href="/mantis"),
                        ],
                    ),
                    # jobs monitoring page
                    dmc.NavLink(label=dmc.Text("Jobs", size="md"), href="/jobs", leftSection=DashIconify(icon="bi:terminal-fill", height=16)),

                    # pages related to thesis analysis and visualizations
                    dmc.Divider(),
                    dmc.NavLink(label=dmc.Text("Dataset Overview", size="md"), href="/dataset_overview", leftSection=DashIconify(icon="bi:database-fill", height=16)),
                    dmc.NavLink(label=dmc.Text("Tool Comparison", size="md"), href="/tool_comparison", leftSection=DashIconify(icon="bi:intersect", height=16)),
                ],
                p="md",
            ),

            # main content area
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

def make_appshell_callbacks():
    @callback(
        Output("appshell", "navbar"),
        Input("burger", "opened"),
        State("appshell", "navbar"),
    )
    def navbar_is_open(opened, navbar):
        # toggle navbar visibility on mobile devices
        navbar["collapsed"] = {"mobile": not opened}
        return navbar


    # client-side callback to toggle Mantine color scheme light/dark
    clientside_callback(
        """
        function(switchOn) {
            document.documentElement.setAttribute(
                "data-mantine-color-scheme",
                switchOn ? "dark" : "light"
            );
            return "";
        }
        """,
        Output("theme-dummy", "children"),
        Input("color-scheme-toggle", "checked"),
    )