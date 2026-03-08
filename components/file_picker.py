from dash import Input, Output, State, callback, ALL, ctx, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash.exceptions import PreventUpdate
import os

class FileTree:
    """
    The original code that inspired me : https://community.plotly.com/t/file-explorer-tree-generator-for-local-files/68732
    """
    def __init__(self, filepath: os.PathLike, query: str = ""):
        self.filepath = filepath
        self.query = (query or "").strip().lower()

    def matches(self, name: str) -> bool:
        if not self.query:
            return True
        return self.query in name.lower()

    def render(self) -> dmc.Accordion:
        return dmc.Accordion(
            self.build_tree(self.filepath, isRoot=True),
            multiple=True,
            chevronPosition="right",
        )

    def flatten(self, nested_list):
        return [item for sublist in nested_list for item in sublist]

    def make_file(self, file_path: str):
        name = os.path.basename(file_path)
        return dmc.Button(
            id={"type": "file", "path": file_path},
            variant="subtle",
            color="blue",
            fullWidth=True,
            justify="flex-start",
            children=dmc.Group(
                gap="xs",
                children=[
                    DashIconify(icon="bi:file-earmark", height=16),
                    dmc.Text(name, size="sm"),
                ],
            ),
        )

    def make_folder(self, folder_name):
        return [DashIconify(icon="bi:folder2"), " ", folder_name]

    def build_tree(self, path, isRoot=False):
        items = []
        if os.path.isdir(path):
            children = self.flatten(
                [
                    self.build_tree(os.path.join(path, subdir)) for subdir in os.listdir(path)
                ]
            )

            folder_name = os.path.basename(path) or str(path)
            folder_value = str(path)

            if self.query and (not self.matches(folder_name)) and (len(children) == 0):
                return []

            item = dmc.AccordionItem(
                value=folder_value,
                children=[
                    dmc.AccordionControl(self.make_folder(folder_name)),
                    dmc.AccordionPanel(children)
                ]
            )

            if isRoot:
                items.append(item)
            else:
                items.append(
                    dmc.Accordion(
                        children=[item],
                        multiple=True,
                        chevronPosition="right",
                    )
                )
        else:
            if self.query and not self.matches(os.path.basename(str(path))):
                return []

            items.append(self.make_file(str(path)))

        return items

def make_file_picker():
    return dmc.Stack(
        children=[
            dmc.Group(
                gap="xs",
                children=[
                    dmc.Button("Browse...", id="modal-file-picker-button", variant="outline"),
                    dmc.ActionIcon(
                        DashIconify(icon="bi:x-lg", height=14),
                        id="clear-selected-file",
                        variant="subtle",
                        color="red",
                        disabled=True,
                    ),
                ],
            ),
            dmc.Modal(
                title="File picker",
                id="modal-file-picker",
                centered=True,
                size="lg",
                children=[
                    dmc.TextInput(
                        id="file-tree-search",
                        placeholder="Search files/folders…",
                        leftSection=DashIconify(icon="bi:search", height=16),
                        mb="sm",
                    ),
                    dcc.Store(id="selected-file"),
                    dcc.Store(id="temp-selected-file"),
                    dmc.Stack(
                        style={"height": 400},
                        children=[
                            dmc.ScrollArea(
                                style={"flex": 1},
                                children=dmc.Stack(id="file-tree-container"),
                            ),
                        ]
                    ),
                    
                    dmc.Text(id="temp-selected-file-label",
                        children="Selected: (none)"
                    ),
                    dmc.Button("Choose file", id="modal-submit-button"),
                ]
            )
        ]
    )

def make_file_picker_callbacks():
    @callback(
        Output("modal-file-picker", "opened", allow_duplicate=True),
        Output("temp-selected-file", "data", allow_duplicate=True),
        Output("temp-selected-file-label", "children", allow_duplicate=True),
        Input("modal-file-picker-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def modal_file_picker(_n):
        return True, None, "Selected: (none)"

    @callback(
        Output("temp-selected-file", "data"),
        Output("temp-selected-file-label", "children"),
        Input({"type": "file", "path": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_file(n_clicks):
        if not n_clicks or all(click is None for click in n_clicks):
            raise PreventUpdate

        tid = ctx.triggered_id
        if not tid:
            return no_update, no_update

        path = tid["path"]
        return path, f"Selected: {path}"

    @callback(
        Output("selected-file", "data"),
        Output("modal-file-picker", "opened"),
        Input("modal-submit-button", "n_clicks"),
        State("temp-selected-file", "data"),
        prevent_initial_call=True,
    )
    def confirm_selection(n_clicks, temp_path):
        if not temp_path:
            return no_update, no_update
        return temp_path, False

    @callback(
        Output("modal-file-picker-button", "children"),
        Output("clear-selected-file", "disabled"),
        Input("selected-file", "data"),
    )
    def update_browse_button(selected):
        if not selected:
            return "Browse...", True

        name = os.path.basename(selected)
        return [DashIconify(icon="bi:file-earmark", height=16), " ", name], False

    @callback(
        Output("selected-file", "data", allow_duplicate=True),
        Output("temp-selected-file", "data", allow_duplicate=True),
        Output("temp-selected-file-label", "children", allow_duplicate=True),
        Input("clear-selected-file", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_selection(_n):
        return None, None, "Selected: (none)"

    @callback(
        Output("file-tree-container", "children"),
        Input("file-tree-search", "value"),
    )
    def update_tree(query):
        return FileTree("/home/danilovd/data", query=query).render()