# MAIN DIR PATHS
logs_path   = "/home/danilovd/logs/"
jobs_path   = "/home/danilovd/jobs2/"
data_path   = "/home/danilovd/data/"
tools_path  = "/home/danilovd/tools/"

# TOOL PATHS

# JOBS OUTPUT
job_output_excluded_extensions = {".log", ".json", ".hist",}
job_output_excluded_files = {}

MAX_OUTPUT_SIZE = 200 * 1024 * 1024 # 200 MiB

# EXTENSIONS
FASTA_EXT = (".fasta", ".fas", ".fa", ".fna", ".ffn", ".faa", ".mpfa", ".frn",)
FASTA_IDX_EXT = (".fai",)
BAM_EXT = (".bam",)
BAM_IDX_EXT = (".bai",)
MICROSAT_LIST_EXT = (".microsatellite.list",)
MICROSAT_LIST_PRO_EXT = (".microsatellite.list.pro",)
BED_EXT = (".bed",)