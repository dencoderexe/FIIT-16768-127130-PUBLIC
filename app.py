import dash
from dash import Dash, html, dcc, Input, Output, State, callback, no_update, clientside_callback
import dash_mantine_components as dmc
from components.appshell import make_appshell, make_appshell_callbacks
from services.job_manager import cleanup_corrupted_jobs

app = Dash(use_pages=True, suppress_callback_exceptions=True)

make_appshell_callbacks()

app.layout = dmc.MantineProvider(
    children=[
        make_appshell(content=dash.page_container),
        dmc.NotificationContainer(id="notification-container"),
    ]
)

def main():
    cleanup_corrupted_jobs()
    app.run(debug=True)

if __name__ == "__main__":
    main()