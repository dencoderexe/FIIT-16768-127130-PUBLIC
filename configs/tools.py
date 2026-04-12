from models.tools import Tool, Command


msi_analysis_commands = ("msi", "pro", "mantis")

TOOLS = {
    "msisensor2": Tool(
        key="msisensor2",
        name="MSIsensor2",
        description=(
            "MSIsensor2 is a machine learning-based tool for microsatellite instability (MSI) detection, "
            "with support for both tumor-only (improved support) and tumor-normal analysis."
        ),
        dir="/home/danilovd/tools/msisensor2/",
        commands={
            "scan": Command(
                key="scan",
                name="scan",
                description=(
                    "MSIsensor2 scan identifies homopolymer and microsatellite loci in a reference genome "
                    "and generates a microsatellite list file for MSI analysis.\n"
                    "It uses the same scanning strategy as the original MSIsensor scan command.\n"
                    "To run the tool, select a reference genome file in FASTA format.\n"
                    "Additional parameters allow you to control which loci are reported:\n"
                    "- Minimum and maximum homopolymer size define the allowed homopolymer length.\n"
                    "- Context length defines how many flanking bases are stored for each site.\n"
                    "- Maximum microsatellite length defines the maximum motif size to search for.\n"
                    "- Minimum microsatellite repeats define how many repeat units are required for a microsatellite to be reported.\n"
                    "- Homopolymer only limits the output to homopolymer sites."
                ),
                template=(
                    "./msisensor2 scan "
                    "-d {reference_genome} "
                    "-o {output} "
                    "-l {min_homo_size} "
                    "-m {max_homo_size} "
                    "-c {context_len} "
                    "-s {max_microsat_len} "
                    "-r {min_microsat_rep} "
                    "-p {homopolymer_only} "
                ),
                steps=[
                    "Scanning reference genome for homopolymers and microsatellites"
                ],
                defaults={
                    "min_homo_size": 5,
                    "max_homo_size": 50,
                    "context_len": 5,
                    "max_microsat_len": 5,
                    "min_microsat_rep": 3,
                    "homopolymer_only": 0,
                },
                link_output_to_input_arg="reference_genome",
            ),
            "msi": Command(
                key="msi",
                name="msi",
                description=(
                    "MSIsensor2 msi performs MSI scoring using a tumor BAM file, with optional support for a matched "
                    "normal BAM file for tumor-normal analysis.\n"
                    "To run the tool, select a model and a tumor BAM file. "
                    "You may optionally provide a matched normal BAM file to run in tumor-normal mode.\n"
                    "A microsatellite list file, BED file, and genomic region can also be provided to limit the analysis "
                    "to specific loci or regions.\n"
                    "Additional parameters allow you to control analysis thresholds and filtering:\n"
                    "- Coverage defines the minimum recommended sequencing depth for analysis.\n"
                    "- Coverage normalization enables normalization for paired tumor-normal analysis.\n"
                    "- FDR threshold controls the false discovery rate used for calling unstable sites.\n"
                    "- Homopolymer and microsatellite size parameters define which loci are included in distribution analysis.\n"
                    "- Span size window defines the window around each site used for read extraction.\n"
                    "- Threads control parallel processing.\n"
                    "- Homopolymer only and microsatellite only restrict the analysis to one locus type.\n"
                    "Tumor-only mode is suitable when no matched normal sample is available, while tumor-normal mode "
                    "can be used when both tumor and matched normal BAM files are provided."
                ),
                template=(
                    "./msisensor2 msi "
                    "-M {model} "
                    "-t {tumor_bam} "
                    "-o {output} "
                    
                    "-f {fdr_threshold} "
                    "-c {coverage} "
                    "-z {coverage_normalization} "
                    "-l {min_homo_size} "
                    "-p {min_homo_size_dist} "
                    "-m {max_homo_size_dist} "
                    "-q {min_microsat_size} "
                    "-s {min_microsat_size_dist} "
                    "-w {max_microsat_size_dist} "
                    "-u {span_size_window} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                ),
                steps=[
                    "Processing user defined region",
                    "Loading BED file",
                    "Loading BAM files",
                    "Checking homopolymer and microsatellite file",
                    "Loading homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "bed_file": None,
                    "fdr_threshold": 0.05,
                    "coverage": 20,
                    "coverage_normalization": 0,
                    "region": None,
                    "min_homo_size": 5,
                    "min_homo_size_dist": 10,
                    "max_homo_size_dist": 50,
                    "min_microsat_size": 3,
                    "min_microsat_size_dist": 5,
                    "max_microsat_size_dist": 40,
                    "span_size_window": 500,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                },
                optionals={
                    "normal_bam": "-n",
                    "bed_file": "-e",
                    "region": "-r",
                    "reference_genome": "-d",
                },
            )
        }
    ),
    "msisensor": Tool(
        key="msisensor",
        name="MSIsensor",
        description=(
            "MSIsensor is a tool for microsatellite instability (MSI) detection that analyzes "
            "repeat length distributions at microsatellite loci using tumor sequencing data, "
            "with optional support for matched normal samples."
        ),
        dir="/home/danilovd/tools/msisensor/",
        commands={
            "scan": Command(
                key="scan",
                name="scan",
                description=(
                    "MSIsensor scan identifies homopolymer and microsatellite loci in a reference genome "
                    "and generates a microsatellite list file for MSI analysis.\n"
                    "To run the tool, select a reference genome file in FASTA format.\n"
                    "Additional parameters allow you to control which loci are reported:\n"
                    "- Minimum and maximum homopolymer size define the allowed homopolymer length.\n"
                    "- Context length defines how many flanking bases are stored for each site.\n"
                    "- Maximum microsatellite length defines the maximum motif size to search for.\n"
                    "- Minimum microsatellite repeats define how many repeat units are required for a microsatellite to be reported.\n"
                    "- Homopolymer only limits the output to homopolymer sites."
                ),
                template=(
                    "./msisensor.linux scan "
                    "-d {reference_genome} "
                    "-o {output} "
                    "-l {min_homo_size} "
                    "-m {max_homo_size} "
                    "-c {context_len} "
                    "-s {max_microsat_len} "
                    "-r {min_microsat_rep} "
                    "-p {homopolymer_only} "
                ),
                steps=[
                    "Scanning reference genome for homopolymers and microsatellites"
                ],
                defaults={
                    "min_homo_size": 5,
                    "max_homo_size": 50,
                    "context_len": 5,
                    "max_microsat_len": 5,
                    "min_microsat_rep": 3,
                    "homopolymer_only": 0,
                },
                link_output_to_input_arg="reference_genome",
            ),
            "msi": Command(
                key="msi",
                name="msi",
                description=(
                    "MSIsensor msi performs MSI scoring using a tumor BAM file and a microsatellite list file, "
                    "with optional support for a matched normal BAM file for tumor-normal analysis.\n"
                    "To run the tool, select a microsatellite list file and a tumor BAM file. "
                    "You may optionally provide a matched normal BAM file to run in tumor-normal mode.\n"
                    "A BED file and genomic region can also be provided to restrict the analysis to specific loci or regions.\n"
                    "Additional parameters allow you to control analysis thresholds and filtering:\n"
                    "- Coverage defines the minimum sequencing depth threshold used for analysis.\n"
                    "- Coverage normalization enables normalization for paired tumor-normal analysis.\n"
                    "- FDR threshold controls the false discovery rate used for calling unstable sites.\n"
                    "- Homopolymer and microsatellite size parameters define which loci are included in distribution analysis.\n"
                    "- Span size window defines the window around each site used for read extraction.\n"
                    "- Threads control parallel processing.\n"
                    "- Homopolymer only and microsatellite only restrict the analysis to one locus type.\n"
                    "MSIsensor was originally designed for paired tumor-normal sequencing data."
                ),
                template=(
                    "./msisensor.linux msi "
                    "-d {microsatellite_list} "
                    "-t {tumor_bam} "
                    "-o {output} "

                    "-f {fdr_threshold} "
                    "-c {coverage} "
                    "-z {coverage_normalization} "
                    "-l {min_homo_size} "
                    "-p {min_homo_size_dist} "
                    "-m {max_homo_size_dist} "
                    "-q {min_microsat_size} "
                    "-s {min_microsat_size_dist} "
                    "-w {max_microsat_size_dist} "
                    "-u {span_size_window} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                ),
                steps=[
                    "Processing user defined region",
                    "Loading BED file",
                    "Loading BAM files",
                    "Checking homopolymer and microsatellite file",
                    "Loading homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "bed_file": None,
                    "fdr_threshold": 0.05,
                    "coverage": 20,
                    "coverage_normalization": 0,
                    "region": None,
                    "min_homo_size": 5,
                    "min_homo_size_dist": 10,
                    "max_homo_size_dist": 50,
                    "min_microsat_size": 3,
                    "min_microsat_size_dist": 5,
                    "max_microsat_size_dist": 40,
                    "span_size_window": 500,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                },
                optionals={
                    "normal_bam": "-n",
                    "bed_file": "-e",
                    "region": "-r",
                },
            ),
        }
    ),
    "msisensor-pro": Tool(
        key="msisensor-pro",
        name="MSIsensor-pro",
        description=(
            "MSIsensor-pro is an updated version of MSIsensor. MSIsensor-pro evaluates "
            "Microsatellite Instability (MSI) for cancer patients with next generation "
            "sequencing data with support for both paired tumor-normal and tumor-only analysis." 
            "It accepts the whole genome sequencing, whole exome sequencing "
            "and target region (panel) sequencing data as input. "
        ),
        dir="/home/danilovd/tools/msisensor-pro/",
        commands={
            "scan": Command(
                key="scan",
                name="scan",
                description=(
                    "MSIsensor-pro scan identifies homopolymer and microsatellite loci in a reference genome "
                    "and generates a microsatellite list file for downstream MSI analysis.\n"
                    "To run the tool, select a reference genome file in FASTA format.\n"
                    "Additional parameters allow you to control which loci are reported:\n"
                    "- Minimum and maximum homopolymer size define the allowed homopolymer length.\n"
                    "- Context length defines how many flanking bases are stored for each site.\n"
                    "- Maximum microsatellite motif length defines the maximum repeat unit size to search for.\n"
                    "- Minimum microsatellite repeats define how many repeat units are required for a microsatellite to be reported.\n"
                    "- Homopolymer only limits the output to homopolymer sites."
                ),
                template=(
                    "./msisensor-pro-v1.3.0 scan "
                    "-d {reference_genome} "
                    "-o {output} "

                    "-l {min_homo_size} "
                    "-m {max_homo_size} "
                    "-c {context_len} "
                    "-s {max_microsat_len} "
                    "-r {min_microsat_rep} "
                    "-p {homopolymer_only} "
                ),
                steps=[
                    "Scanning reference genome for homopolymers and microsatellites"
                ],
                defaults={
                    "min_homo_size": 8,
                    "max_homo_size": 50,
                    "context_len": 5,
                    "max_microsat_len": 6,
                    "min_microsat_rep": 5,
                    "homopolymer_only": 0,
                },
                link_output_to_input_arg="reference_genome",
            ),
            "msi": Command(
                key="msi",
                name="msi",
                description=(
                    "MSIsensor-pro msi performs MSI scoring using paired normal and tumor BAM files.\n"
                    "To run the tool, select a microsatellite list file, a matched normal BAM file, and a tumor BAM file.\n"
                    "An optional BED file can be provided to restrict the analysis to specific loci or regions.\n"
                    "Additional parameters allow you to control analysis thresholds and filtering:\n"
                    "- Coverage defines the sequencing depth threshold used for MSI analysis.\n"
                    "- Coverage normalization enables normalization for paired tumor-normal analysis.\n"
                    "- FDR threshold controls somatic unstable site detection.\n"
                    "- Homopolymer and microsatellite size parameters define which loci are included in distribution analysis.\n"
                    "- Span size window defines the window around each site used for read extraction.\n"
                    "- Threads control parallel processing.\n"
                    "- Homopolymer only and microsatellite only restrict the analysis to one locus type.\n"
                    "- Include sites with no read coverage controls whether zero-coverage sites are retained in the output."
                ),
                template=(
                    "./msisensor-pro-v1.3.0 msi "
                    "-d {microsatellite_list} "
                    "-n {normal_bam} "
                    "-t {tumor_bam} "
                    "-o {output} "

                    "-f {fdr_threshold} "
                    "-c {coverage} "
                    "-z {coverage_normalization} "
                    "-p {min_homo_size_dist} "
                    "-m {max_homo_size_dist} "
                    "-s {min_microsat_size_dist} "
                    "-w {max_microsat_size_dist} "
                    "-u {span_size_window} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                    "-0 {include_zero_coverage_sites} "
                ),
                steps=[
                    "Processing user defined region",
                    "Loading BED file",
                    "Loading BAM files",
                    "Checking homopolymer and microsatellite file",
                    "Loading homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "bed_file": None,
                    "fdr_threshold": 0.05,
                    "coverage": 15,
                    "coverage_normalization": 0,
                    "min_homo_size_dist": 8,
                    "max_homo_size_dist": 50,
                    "min_microsat_size_dist": 5,
                    "max_microsat_size_dist": 40,
                    "span_size_window": 500,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                    "include-zero-coverage-sites": 1,
                },
                optionals={
                    "bed_file": "-e",
                }
            ),
            "pro": Command(
                key="pro",
                name="pro",
                description=(
                    "MSIsensor-pro pro performs MSI scoring using a single tumor sample without a matched normal BAM file.\n"
                    "To run the tool, select a microsatellite list file and a tumor BAM file.\n"
                    "An optional BED file can be provided to restrict the analysis to specific loci or regions.\n"
                    "Additional parameters allow you to control analysis thresholds and filtering:\n"
                    "- Unstable sites threshold defines the minimum threshold used for unstable site detection in tumor-only analysis.\n"
                    "- Coverage defines the sequencing depth threshold used for MSI analysis.\n"
                    "- Homopolymer and microsatellite size parameters define which loci are included in distribution analysis.\n"
                    "- Span size window defines the window around each site used for read extraction.\n"
                    "- Threads control parallel processing.\n"
                    "- Homopolymer only and microsatellite only restrict the analysis to one locus type.\n"
                    "- Include sites with no read coverage controls whether zero-coverage sites are retained in the output."
                ),
                template=(
                    "./msisensor-pro-v1.3.0 pro "
                    "-d {microsatellite_list} "
                    "-t {tumor_bam} "
                    "-o {output} "

                    "-i {instable_sites_threshold} "
                    "-c {coverage} "
                    "-p {min_homo_size_dist} "
                    "-m {max_homo_size_dist} "
                    "-s {min_microsat_size_dist} "
                    "-w {max_microsat_size_dist} "
                    "-u {span_size_window} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                    "-0 {out_site_no_read_coverage} "
                ),
                steps=[
                    "Loading BAM files",
                    "Loading BED file",
                    "Checking homopolymer and microsatellite file",
                    "Loading homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "bed_file": None,
                    "instable_sites_threshold": 0.1,
                    "coverage": 15,
                    "min_homo_size_dist": 8,
                    "max_homo_size_dist": 50,
                    "min_microsat_size_dist": 5,
                    "max_microsat_size_dist": 40,
                    "span_size_window": 500,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                    "out_site_no_read_coverage": 1,
                },
                optionals={
                    "bed_file": "-e",
                }
            )
        }
    ),
    "mantis": Tool(
        key="mantis",
        name="MANTIS",
        description=(
            "MANTIS (Microsatellite Analysis for Normal-Tumor InStability) is a program "
            "developed for detecting microsatellite instability from paired-end BAM files. "
            "To perform analysis, the program needs a tumor BAM and a matched normal BAM file "
            "(produced using the same pipeline) to determine the instability score between the "
            "two samples within the pair."
        ),
        dir="/home/danilovd/tools/MANTIS-1.0.5/",
        commands={
            "mantis": Command(
                key="mantis",
                name="mantis",
                description=(
                    "To run the tool, select normal and tumor BAM files generated using the same pipeline, "
                    "a reference genome in FASTA format, and a BED file with microsatellite loci.\n"
                    "The BED file can be generated using the RepeatFinder (tool included with MANTIS), "
                    "or by using our Microsat2Bed tool to convert microsatellite lists produced by MSIsensor.\n"
                    "Additional parameters allow you to control quality filtering and analysis thresholds:\n"
                    "- Threads control parallel processing.\n"
                    "- Minimum read quality and locus quality define quality control thresholds.\n"
                    "- Minimum read length filters out short or clipped reads.\n"
                    "- Minimum locus coverage defines how many reads are required in both samples.\n"
                    "- Minimum repeat reads control support required for repeat counts.\n"
                    "- Standard deviations define how outliers are filtered from repeat distributions.\n"
                    "Longer reads (ideally >= 100 bp) are recommended, as shorter reads may not fully cover "
                    "microsatellite loci and can be removed during quality control."
                ),
                template=(
                    "/home/danilovd/.conda/envs/mantis/bin/python -u ./mantis.py "
                    "-n {normal_bam} "
                    "-t {tumor_bam} "
                    "--genome {reference_genome} "
                    "-b {bed_file} "
                    "-o {output} "

                    "--threads {threads} "
                    "--min-read-quality {min_read_quality} "
                    "--min-locus-quality {min_locus_quality} "
                    "--min-read-length {min_read_length} "
                    "--min-locus-coverage {min_locus_coverage} "
                    "--min-repeat-reads {min_repeat_reads} "
                    "--standard-deviations {standard_deviations} "
                ),
                steps=[
                    "Computing k-mer repeat counts",
                    "Filtering outlier k-mer counts",
                    "Calculating instability scores",
                ],
                defaults={
                    "threads": 1,
                    "min_read_quality": 25.0,
                    "min_locus_quality": 30.0,
                    "min_read_length": 35,
                    "min_locus_coverage": 30,
                    "min_repeat_reads": 3,
                    "standard_deviations": 3.0,
                },
            )
        }
    ),
    "repeatfinder": Tool(
        key="repeatfinder",
        name="RepeatFinder",
        description=(
            "RepeatFinder is a tool included with MANTIS for detecting microsatellite "
            "regions in a reference genome and generating a BED file for MSI analysis."
        ),
        dir="/home/danilovd/tools/MANTIS-1.0.5/tools/",
        commands={
            "repeatfinder": Command(
                key="repeatfinder",
                name="repeatfinder",
                description=(
                    "RepeatFinder scans a reference genome in FASTA format and identifies microsatellite regions, "
                    "generating a BED file compatible with MANTIS.\n"
                    "To run the tool, select a reference genome file from the list on the left. "
                    "Additional parameters allow you to control which microsatellite regions are reported:\n"
                    "- Minimum and maximum repeat region length define the allowed size of detected microsatellites.\n"
                    "- Minimum k-mer repeats specify how many motif repetitions are required.\n"
                    "- Minimum and maximum k-mer length define the motif sizes to search for.\n"
                    "The default maximum k-mer length is 5, as larger values may include telomeric repeats."
                ),
                template=(
                    "./RepeatFinder "
                    "-i {reference_genome} "
                    "-o {output} "

                    "-m {min_length} "
                    "-M {max_length} "
                    "-r {min_repeats} "
                    "-l {min_kmer} "
                    "-L {max_kmer} "
                ),
                steps=[
                    "Scanning reference genome for microsatellite regions",
                ],
                defaults={
                    "min_length": 10,
                    "max_length": 100,
                    "min_repeats": 3,
                    "min_kmer": 1,
                    "max_kmer": 5,
                },
                link_output_to_input_arg="reference_genome",
            )
        }
    ),
    "samtools": Tool(
        key="samtools",
        name="Samtools",
        description=(
            "SAMtools is a set of utilities for interacting with and processing "
            "sequence alignment files in SAM, BAM and CRAM formats."
        ),
        dir="/home/danilovd/tools/",
        commands={
            "index": Command(
                key="index",
                name="index",
                description=(
                    "Samtools index creates an index for a BAM file to enable fast random access "
                    "to alignment data.\n"
                    "To run the command, select a BAM file. The resulting index file (.bai) allows "
                    "efficient querying of specific genomic regions without reading the entire file."
                ),
                template=(
                    "samtools index --bai "
                    "{bam_file} "
                    "-o {output} "
                ),
                steps=[
                    "Indexing BAM file",
                ],
                optionals={
                    "threads": "--threads"
                },
                link_output_to_input_arg="bam_file",
            ),
            "sort": Command(
                key="sort",
                name="sort",
                description=(
                    "Samtools sort sorts a BAM file by genomic coordinates or read name.\n"
                    "To run the command, select a BAM file. Sorting is typically required before indexing "
                    "and for many downstream analyses.\n"
                    "By default, sorting is performed by genomic coordinates."
                ),
                template=(
                    "samtools sort "
                    "{bam_file} "
                    "-o {output} "
                ),
                steps=[
                    "Sorting BAM file",
                ],
                optionals={
                    "threads": "--threads"
                },
                link_output_to_input_arg="bam_file",
            ),
            "merge": Command(
                key="merge",
                name="merge",
                description=(
                    "Samtools merge combines multiple sorted BAM files into a single output BAM file.\n"
                    "To run the command, select multiple BAM files. All input files should be sorted "
                    "by genomic coordinates.\n"
                    "The resulting file can optionally be indexed during the merge process."
                ),
                template=(
                    "samtools merge "
                    "-o {output} "
                    "{bam_files} "
                ),
                steps=[
                    "Merging BAM files",
                ],
                optionals={
                    "threads": "--threads",
                },
                link_output_to_input_arg="save_next_to",
            ),
            "faidx": Command(
                key="faidx",
                name="faidx",
                description=(
                    "Samtools faidx indexes a FASTA reference genome file.\n"
                    "To run the command, select a FASTA file. The generated index (.fai) allows "
                    "fast random access to specific regions of the reference genome."
                ),
                template=(
                    "samtools faidx "
                    "{reference_genome} "
                    "-o {output} "
                ),
                steps=[
                    "Indexing FASTA file",
                ],
                optionals={
                    "threads": "--threads"
                },
                link_output_to_input_arg="reference_genome",
            ),
            "stats": Command(
                key="stats",
                name="stats",
                description=(
                    "Samtools stats generates comprehensive statistics from a BAM file.\n"
                    "To run the command, select a BAM file. The output includes information such as "
                    "total reads, mapped reads, coverage, insert size distribution, and quality metrics.\n"
                    "The resulting report can be used for quality control and downstream analysis."
                ),
                template=(
                    "samtools stats "
                    "{bam_file} "
                    "> {output} "
                ),
                steps=[
                    "Producing comprehensive statistics from alignment file",
                ],
                optionals={
                    "threads": "--threads"
                },
            ),
        }
    ),
    "microsat2bed": Tool(
        key="microsat2bed",
        name="Microsat2Bed",
        description=(
            "Microsat2Bed is our tool for converting MSIsensor microsatellite lists into BED format "
            "compatible with MANTIS and RepeatFinder coordinate conventions."
        ),
        dir="/home/danilovd/tools/",
        commands={
            "convert": Command(
                key="convert",
                name="convert",
                description=(
                    "Microsat2Bed converts a microsatellite list generated by MSIsensor scan into "
                    "a BED file compatible with MANTIS.\n"
                    "To run the tool, select a microsatellite list file. "
                    "Note: MSIsensor-pro microsatellite lists are not supported; use MSIsensor only.\n"
                    "The output BED file follows RepeatFinder coordinate conventions and can be used as input for MANTIS.\n"
                    "This enables the use of the same reference loci across tools such as MSIsensor and MANTIS, "
                    "supporting more consistent cross-tool comparison."
                ),
                template=(
                    "python -u microsat2bed.py "
                    "{microsatellite_list} "
                    "{output} "
                ),
                steps=[
                    "Generating BED file from microsatellite list",
                ],
                link_output_to_input_arg="microsatellite_list",
            ),
        }
    )
}