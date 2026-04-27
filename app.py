import os

# https://stackoverflow.com/a/53224849
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from dash import Dash

import dash
import dash_mantine_components as dmc

from components.appshell import make_appshell, make_appshell_callbacks
from services.job_manager import cleanup_corrupted_jobs, start_job_resource_monitor, get_finished_jobs
from services.logger import setup_logging

# initialize Dash app with multi-page suppor
app = Dash(use_pages=True, suppress_callback_exceptions=True)

# register global AppShell callbacks (navbar toggle, theme switch)
make_appshell_callbacks()

app.layout = dmc.MantineProvider(
    children=[
        # main app layout
        make_appshell(content=dash.page_container),

        # global notification container
        dmc.NotificationContainer(id="notification-container"),
    ]
)

def main():
    setup_logging()
    cleanup_corrupted_jobs()
    start_job_resource_monitor()

    get_finished_jobs()

    # define run parameters and start app
    app.run(host="0.0.0.0", port=8050, debug=True)

if __name__ == "__main__":
    main()
