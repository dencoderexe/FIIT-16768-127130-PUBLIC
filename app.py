from dash import Dash

import dash
import dash_mantine_components as dmc

from components.appshell import make_appshell, make_appshell_callbacks
from services.job_manager import cleanup_corrupted_jobs, start_job_memory_monitor
from services.logger import setup_logging

app = Dash(use_pages=True, suppress_callback_exceptions=True)

make_appshell_callbacks()

app.layout = dmc.MantineProvider(
    children=[
        make_appshell(content=dash.page_container),
        dmc.NotificationContainer(id="notification-container"),
    ]
)

def main():
    setup_logging()
    cleanup_corrupted_jobs()
    start_job_memory_monitor()

    app.run(host="0.0.0.0", port=8050, debug=False)

if __name__ == "__main__":
    main()
