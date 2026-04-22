import pandas as pd
import plotly.graph_objects as go

from configs.tools import TOOLS

mantis_treshold = TOOLS["mantis"].commands["mantis"].msi_threshold

def parse_unstable_loci_msisensor(unstable_file: str) -> pd.DataFrame:      
    """
    Parse MSIsensor/2/pro output file with unstable loci and return them as df
    """ 
    df = pd.read_csv(unstable_file, sep="\t", header=None, usecols=[0, 1], dtype=str)

    if not str(df.iloc[0, 1]).isdigit():    # check if output file has column names at the beginning
        df = df.iloc[1:]                    # skip first row with column names

    df.columns = ["chromosome", "start"]
    df["start"] = df["start"].astype(int)   # convert str to int

    return df

def parse_unstable_loci_mantis(unstable_file: str, threshold: int) -> pd.DataFrame:
    """
    Parse MANTIS output file with unstable loci and return them as df
    """ 
    def parse_locus(locus: str) -> tuple(str, int, int):
        chromosome, coords = locus.split(":")
        start, end = map(int, coords.split("-"))
        return chromosome, start-1

    df = pd.read_csv(unstable_file, sep="\t", usecols=["Locus", "Difference"])
    df = df.iloc[:-1]                       # remove last entry with average calculations
    df = df[df["Difference"] > threshold]
    df[["chromosome", "start"]] = df["Locus"].apply(
        lambda x: pd.Series(parse_locus(x))
    )
    df = df.drop(columns=["Locus", "Difference"])
    return df

def jaccard_index_heatmap(data: list[dict], patient: str) -> go.Figure:
    """
    Compute and visualize pairwise similarity between MSI tools using the Jaccard index.

    Each tool produces a set of unstable loci (chromosome, position). This function:
    1) Parses loci from tool output files
    2) Converts them into sets of genomic coordinates
    3) Computes pairwise Jaccard index:
        J(A, B) = |A and B| / |A or B|
    4) Builds a heatmap showing overlap between all tool combinations

    Parameters:
        data : list[dict]
            Each dictionary must contain:
            - tool (str): Tool name (e.g. "MSIsensor", "MANTIS")
            - mode (str): Mode of operation (e.g. "Tumor-only", "Tumor-normal")
            - output (str): Path to unstable loci output file
        patient : str
            Patient identifier used in the plot title.

    Returns:
        go.Figure
            Plotly heatmap figure where:
                - axes represent tools
                - cell values represent Jaccard similarity [0, 1]
                - hover shows intersection, union, and set sizes

    Notes:
    - For MANTIS, loci are filtered using a predefined MSI threshold.
    - For MSIsensor-based tools, loci are read directly from output files.
    - Coordinates are normalized to (chromosome, start) tuples.
    - If both sets are empty, Jaccard index is defined as 1.0.

    Interpretation:
    - 1.0 -> identical loci sets
    - 0.0 -> no overlap
    - Other values -> partial agreement between tools
    """
    def parse_unstable_loci(tool: dict) -> set[tuple[str, int]]:
        tool_name = tool["tool"]
        output_file = tool["output"]

        if tool_name == "MANTIS":
            df = parse_unstable_loci_mantis(output_file, mantis_treshold)
        else:
            df = parse_unstable_loci_msisensor(output_file)

        # convert df to set of tuples
        return set(df[["chromosome", "start"]].itertuples(index=False, name=None))

    labels = [f'{tool["tool"]} ({tool["mode"]})' for tool in data]
    loci_sets = [parse_unstable_loci(tool) for tool in data]

    # matrix of Jaccard values
    z_matrix = []

    hover_texts_matrix = []

    for i, set_a in enumerate(loci_sets):
        z_row = []
        hover_text_row = []

        for j, set_b in enumerate(loci_sets):
            union = set_a | set_b
            intersection = set_a & set_b

            jaccard = len(intersection) / len(union) if union else 1.0

            z_row.append(jaccard)
            hover_text_row.append(
                "<br>".join([
                    f"{labels[i]} vs {labels[j]}",
                    f"Jaccard index: {jaccard:.3f}",
                    f"Intersection: {len(intersection)}",
                    f"Union: {len(union)}",
                    f"|A|: {len(set_a)}",
                    f"|B|: {len(set_b)}",
                ])
            )

        z_matrix.append(z_row)
        hover_texts_matrix.append(hover_text_row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_matrix,
            x=labels,
            y=labels,
            zmin=0,
            zmax=1,
            colorscale="Viridis",
            text=hover_texts_matrix,
            hoverinfo="text",
            texttemplate="%{z:.2f}",
            textfont={"size": 16},
            colorbar=dict(
                title=dict(text="Jaccard", font=dict(size=16)),
                tickfont=dict(size=16)
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=f"{patient} - Jaccard index heatmap of unstable loci",
            x=0.5,
            xanchor="center",
        ),
        xaxis_title="Tool B",
        yaxis_title="Tool A",
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
        template="plotly_dark",
        height=700,
        margin={"l": 10, "r": 10, "t": 80, "b": 40},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    fig.update_xaxes(
        tickfont=dict(size=16),
        side="bottom",
    )

    fig.update_yaxes(
        tickfont=dict(size=16),
        autorange="reversed",
        scaleanchor="x",
        scaleratio=1,
    )

    return fig