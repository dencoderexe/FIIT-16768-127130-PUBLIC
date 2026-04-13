from dash_iconify import DashIconify

def job_started_notification(message: str) -> dict:
    return [dict(
        title="Job started",
        action="show",
        color="yellow",
        message=str(message),
        autoClose=3000,
        icon=DashIconify(icon="bi:arrow-repeat"),
    )]

def job_started_failed_notification(message: str) -> dict:
    return [dict(
        title="Failed to start job",
        action="show",
        color="red",
        message=str(message),
        autoClose=3000,
        icon=DashIconify(icon="bi:x-circle-fill"),
    )]