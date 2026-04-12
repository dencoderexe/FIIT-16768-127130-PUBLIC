from dash_iconify import DashIconify

from models.jobs import Step

import dash_mantine_components as dmc

def step_row(step: Step):
    # Step:                 Started at:     Finished at:
    # status icon + name    datetime        datetime/progress bar
    return dmc.Grid(
        align="center",
        children=[
            dmc.GridCol(
                dmc.Group(
                    gap="sm",
                    wrap="nowrap",
                    children=[
                        dmc.ThemeIcon(
                            DashIconify(icon=step.status.icon, height=14),
                            color=step.status.color,
                            variant="light",
                            radius="xl",
                            size="sm",
                        ),
                        dmc.Text(step.name, size="sm"),
                    ],
                ),
                span=6,
            ),
            dmc.GridCol(
                dmc.Text(
                    step.started_at.strftime("%d.%m.%Y %H:%M:%S") if step.started_at else "-",
                    size="xs",
                    c="dimmed",
                ),
                span=3,
                style={"textAlign": "center"},
            ),
            dmc.GridCol(
                dmc.Group(
                    gap="xs",
                    justify="center",
                    wrap="nowrap",
                    children=[
                        *(
                            [
                                dmc.Progress(
                                    color="yellow",
                                    size="md",
                                    value=int((step.progress_current / step.progress_total) * 100) if step.progress_total else 0,
                                    w=110,
                                    animated=True,
                                )
                            ]
                            if not step.finished_at
                            and step.progress_current is not None
                            and step.progress_total is not None
                            else [
                                dmc.Text(
                                    step.finished_at.strftime("%d.%m.%Y %H:%M:%S") if step.finished_at else "-",
                                    size="xs",
                                    c="dimmed",
                                ),
                            ]
                        ),
                    ],
                ),
                span=3,
            ),
        ],
    )