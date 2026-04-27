# MAIN DIR PATHS
logs_path   = "/home/danilovd/logs/"
jobs_path   = "/home/danilovd/jobs2/"
data_path   = "/home/danilovd/data/"
# logs_path   = "/logs/"
# jobs_path   = "/jobs/"
# data_path   = "/data/"

# TOOL PATHS

# JOBS OUTPUT
job_output_excluded_extensions = {".log", ".json", ".hist", ".zip", ".tmp",}
job_output_excluded_files = {}

MAX_OUTPUT_SIZE = 250 * 1024 * 1024 # 250 MiB

# EXTENSIONS
FASTA_EXT = (".fasta", ".fas", ".fa", ".fna", ".ffn", ".faa", ".mpfa", ".frn",)
FASTA_IDX_EXT = (".fai",)
BAM_EXT = (".bam",)
BAM_IDX_EXT = (".bai",)
MICROSAT_LIST_EXT = (".ms.list",)
MICROSAT_LIST_PRO_EXT = (".ms.list.pro",)
BED_EXT = (".bed",)
MSISENSOR2_MODELS = (".msisensor2.model",)