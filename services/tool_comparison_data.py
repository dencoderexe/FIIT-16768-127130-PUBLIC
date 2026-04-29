import os
import json
import pandas as pd

from pandas.errors import EmptyDataError
from services.job_manager import get_brief_report
from models.jobs import Job

comparison_data_dir = "experiment_data/"

def parse_unstable_loci_msisensor(unstable_file: str) -> pd.DataFrame:      
    """
    Parse MSIsensor/2/pro output file with unstable loci and return them as df
    """ 
    try:
        df = pd.read_csv(unstable_file, sep="\t", header=None, usecols=[0, 1], dtype=str)
    except EmptyDataError:
        return pd.DataFrame(columns=["chromosome", "start"])
    
    if df.empty:
        return pd.DataFrame(columns=["chromosome", "start"])

    if not str(df.iloc[0, 1]).isdigit():    # check if output file has column names at the beginning
        df = df.iloc[1:]                    # skip first row with column names

    if df.empty:
        return pd.DataFrame(columns=["chromosome", "start"])

    df.columns = ["chromosome", "start"]
    df["start"] = df["start"].astype(int)   # convert str to int

    return df

def parse_unstable_loci_mantis(unstable_file: str, threshold: int = 1) -> pd.DataFrame:
    """
    Parse MANTIS output file with unstable loci and return them as df
    """
    def parse_locus(locus: str) -> tuple[str, int, int]:
        chromosome, coords = locus.split(":")
        start, end = map(int, coords.split("-"))
        return chromosome, start-1

    try:
        df = pd.read_csv(unstable_file, sep="\t", usecols=["Locus", "Difference"])
    except EmptyDataError:
        return pd.DataFrame(columns=["chromosome", "start"])

    if df.empty:
        return pd.DataFrame(columns=["chromosome", "start"])
    
    df = df.iloc[:-1]                       # remove last entry with average calculations
    if df.empty:
        return pd.DataFrame(columns=["chromosome", "start"])
    
    df = df[df["Difference"] > threshold]
    if df.empty:
        return pd.DataFrame(columns=["chromosome", "start"])
    
    df[["chromosome", "start"]] = df["Locus"].apply(
        lambda x: pd.Series(parse_locus(x))
    )
    df = df.drop(columns=["Locus", "Difference"])
    return df

def build_jaccard_heatmap_data(data: list[dict]) -> dict:
    """
    Compute pairwise similarity between MSI tools using the Jaccard similarity index.

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

    Returns:
        dict
            JSON-serializable heatmap data with:
            - labels: Tool labels used for heatmap axes.
            - matrix: Pairwise Jaccard similarity values.
            - details: Per-cell metadata for hover text, including intersection,
            union, and individual set sizes.

    Notes:
    - For MANTIS, loci are filtered using a predefined MSI threshold == 1.
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
            df = parse_unstable_loci_mantis(output_file)
        else:
            df = parse_unstable_loci_msisensor(output_file)

        if df.empty:
            return set()

        # convert df to set of tuples
        return set(df[["chromosome", "start"]].itertuples(index=False, name=None))

    labels = [f'{tool["tool"]} ({tool["mode"]})' for tool in data]
    loci_sets = [parse_unstable_loci(tool) for tool in data]

    matrix = []
    details = []

    for i, set_a in enumerate(loci_sets):
        matrix_row = []
        details_row = []

        for j, set_b in enumerate(loci_sets):
            union = set_a | set_b
            intersection = set_a & set_b
            jaccard = len(intersection) / len(union) if union else 1.0

            matrix_row.append(jaccard)
            details_row.append({
                "tool_a": labels[i],
                "tool_b": labels[j],
                "jaccard": jaccard,
                "intersection": len(intersection),
                "union": len(union),
                "set_a": len(set_a),
                "set_b": len(set_b),
            })

        matrix.append(matrix_row)
        details.append(details_row)

    return {
        "labels": labels,
        "matrix": matrix,
        "details": details,
    }

def build_comparison_data_from_jobs(comparison_group_dir: str) -> dict[str, list[dict]]|None:
    """
    Loads jobs from a comparison group directory and builds summary data per patient.

    Each job directory must contain a JSON file with job metadata.

    Returns a dict mapping patients to lists of job summaries, or None if directory does not exist.
    """
    data_dir = os.path.join(comparison_data_dir, comparison_group_dir)

    if not os.path.exists(data_dir):
        return None

    loaded_jobs: list[Job] = []

    for item in os.listdir(data_dir):
        job_dir = os.path.join(data_dir, item)

        if not os.path.isdir(job_dir):
            continue

        file = os.path.join(job_dir, f"{item}.json")
        if not os.path.isfile(file):
            continue

        try:
            loaded_jobs.append(Job.deserialize(file))
        except Exception as e:
            print(f"Failed to load job {item}: {e}")

    patients = sorted({job.args["output"] for job in loaded_jobs})
    data = {}

    for p in patients:
        patient = []

        for job in loaded_jobs:
            if job.args["output"] != p:
                continue

            tool = job.tool.name
            mode = job.get_mode()
            input_loci, analyzed_loci, unstable_loci, msi_status, _ = get_brief_report(job)

            # different tools produce different unstable loci output files
            if tool == "MANTIS":
                output = job.args["output"]
            elif tool in ("MSIsensor", "MSIsensor2"):
                output = f'{job.args["output"]}_somatic'
            elif tool == "MSIsensor-pro":
                output = f'{job.args["output"]}_unstable'
            else:
                continue

            patient.append({
                "tool": tool,
                "mode": mode,
                "msi_status": msi_status,
                "unstable_loci": unstable_loci,
                "analyzed_loci": analyzed_loci,
                "runtime": int((job.finished_at - job.started_at).total_seconds()),
                "max_memory": job.max_memory_usage,
                "input_loci": input_loci,
                "output": os.path.join(job.job_dir, output),
            })

        patient.sort(key=lambda entry: entry["tool"])
        data[p] = patient

    return data

def get_comparison_data(comparison_group_dir: str) -> dict[str, list[dict]]|None:
    """
    Deserialize JSON file with tool comparizon data
    """
    file = os.path.join(comparison_data_dir, comparison_group_dir, "data.json")

    if not os.path.isfile(file):
        return None

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_heatmap_data(comparison_group_dir: str) -> dict|None:
    """
    Deserialize JSON file with tool Jacard index heatmap data
    """
    file = os.path.join(comparison_data_dir, comparison_group_dir, "heatmap.json")

    if not os.path.isfile(file):
        return None

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def export_comparison_data(comparison_group_dir: str) -> None:
    """
    Deserialize tool comparizon data as JSON file
    """
    data = build_comparison_data_from_jobs(comparison_group_dir)

    if data is None:
        print(f"No comparison data found for group {comparison_group_dir}")
        return

    group_dir = os.path.join(comparison_data_dir, comparison_group_dir)
    output_file = os.path.join(group_dir, "data.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Exported comparison data to {output_file}")

def export_heatmap_data(comparison_group_dir: str) -> None:
    """
    Serialize tool Jacard index heatmap data as JSON file
    """
    data = build_comparison_data_from_jobs(comparison_group_dir)

    if data is None:
        print(f"No comparison data found for group {comparison_group_dir}")
        return

    heatmaps = {}

    for patient, tools in data.items():
        heatmaps[patient] = build_jaccard_heatmap_data(tools)

    group_dir = os.path.join(comparison_data_dir, comparison_group_dir)
    output_file = os.path.join(group_dir, "heatmap.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(heatmaps, f, indent=2, ensure_ascii=False)

    print(f"Exported heatmap data to {output_file}")


# python -m services.tool_comparison_data
def export_all_comparison_data() -> None:
    export_comparison_data("g1")
    export_comparison_data("g2")
    export_heatmap_data("g2")

if __name__ == "__main__":
    export_all_comparison_data()