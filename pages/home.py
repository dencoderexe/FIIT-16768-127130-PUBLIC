import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/")

layout = dmc.Container(
    [
        dmc.Title("MSI Pipeline Dashboard", order=1),

        dmc.Space(h="md"),

        dmc.Text(
            "Welcome to the MSI Pipeline Dashboard. This project was developed as part of the bachelor thesis "
            "\"Analysis of Microsatellite Instability in Data from Patients with Lynch Syndrome\". "
            "The dashboard was designed to simplify the execution of MSI-related tools, support the preparation "
            "of input data, and provide a more convenient way to review analysis results.",
            size="md",
        ),

        dmc.Space(h="md"),

        dmc.Text(
            "The application should be understood as a working prototype or MVP (Minimum viable product). It was used during the experimental "
            "part of the thesis to support analysis, testing, and comparison of different tools, while also serving "
            "as a proof of concept for a more complete system.",
            size="md",
        ),

        dmc.Space(h="md"),

        dmc.Text(
            "The dashboard is divided into two main parts. The first part provides the functional interface for running tools, "
            "managing data, and monitoring submitted jobs. The second part presents selected experimental results obtained within the "
            "thesis, together with an overview of the datasets and analysis setup.",
            size="md",
        ),

        dmc.Space(h="md"),

        dmc.Text(
            "Navigation is available via the sidebar on the left, which is organized into logical sections:\n"
            "- Functional part: Home, Tools, Jobs\n"
            "- Summary of experiments: Dataset Overview, Tool Comparison",
            size="md",
            style={"whiteSpace": "pre-line"},
        ),

        dmc.Space(h="md"),

        dmc.Title("Core functionality", order=3),

        dmc.Text(
            "The Tools section simplifies working with preprocessing and MSI analysis tools that are originally "
            "designed to be used from the command line. It provides a graphical interface for configuring and running "
            "selected commands, making it easier to prepare input data, choose files, and specify parameters.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "Although these pages do not provide full documentation for each tool, they include links to the original "
            "resources where detailed information can be found. In addition, each tool page contains a short description "
            "of the tool, its available commands, and their parameters, together with small hints that help guide the user "
            "when selecting inputs and configuring execution options.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "The Jobs page serves as a central control panel for all submitted tasks. It displays active and finished jobs, "
            "their status, step-by-step progress, runtime, CPU and memory usage, execution parameters, logs, and output files.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "Jobs are automatically grouped into active and finished categories. The page updates automatically, allowing "
            "near real-time monitoring without manual refresh. Filtering options help locate jobs by tool, command, status, "
            "or output.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "For completed jobs, additional actions become available:\n"
            "- View logs to inspect execution details or errors\n"
            "- Download output files within the configured size limit\n"
            "- Open a dedicated Results page for MSI analysis jobs",
            size="md",
            style={"whiteSpace": "pre-line"},
        ),

        dmc.Space(h="md"),

        dmc.Title("Results inspection", order=3),

        dmc.Text(
            "The Results page presents a completed MSI analysis job in a standardized and more readable form. "
            "It includes basic job information, selected run parameters, executed steps, and a brief MSI report.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "The output is processed into a unified format independent of the underlying tool. "
            "It includes consistent visualizations such as loci classification, as well as CPU and memory usage over time. "
            "This standardization simplifies interpretation and enables direct comparison between runs.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "Results pages are available only for MSI analysis tools.",
            size="md",
        ),

        dmc.Space(h="md"),

        dmc.Title("Experimental results", order=3),

        dmc.Text(
            "The Dataset Overview page summarizes the data used in the thesis, including input sequencing files, "
            "preprocessed BAM files, tested reference genomes, and loci source files.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "The Tool Comparison page presents selected experiment results, including summaries across patients and "
            "Jaccard similarity heatmaps used to compare unstable loci detected by different tools.",
            size="md",
        ),

        dmc.Space(h="sm"),

        dmc.Text(
            "For detailed explanations of datasets, experimental setup, and result interpretation, please refer directly "
            "to the corresponding pages within the dashboard.",
            size="md",
        ),

        dmc.Space(h="md"),

        dmc.Title("Project repository", order=3),

        dmc.Text(
            [
                "The full source code of this project is available on GitHub: ",
                dmc.Anchor("https://github.com/dencoderexe/FIIT-16768-127130", href="https://github.com/dencoderexe/FIIT-16768-127130", target="_blank"),
                ".",
            ],
            size="md",
        ),
    ],
    fluid=True,
    p="md",
)