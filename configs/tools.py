from models.tools import Tool, Command

TOOLS = {
    "msisensor2": Tool(
        key="msisensor2",
        name="MSIsensor2",
        description=(
            "MSIsensor2 is a novel algorithm based machine learning, featuring a large "
            "upgrade in the microsatellite instability (MSI) detection for tumor only "
            "sequencing data, including Cell-Free DNA (cfDNA), Formalin-Fixed "
            "Paraffin-Embedded(FFPE) and other sample types. The original MSIsensor is "
            "specially designed for tumor/normal paired sequencing data."
        ),
        dir="/home/danilovd/tools/msisensor2/", #TODO
        commands={
            "msi": Command(
                key="msi",
                name="msi",
                description="msi scoring",
                template=(
                    "./msisensor2 msi "
                    "-M {model} "
                    "-t {tumor_bam} "
                    "-o {output} "
                    "-c {coverage} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                ),
                steps=[
                    "Load .BAM files",
                    "Load homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "coverage": 20,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                }
            )
        }
    ),
    "msisensor": Tool(
        key="msisensor",
        name="MSIsensor",
        description=(
            "MSIsensor is a C++ program to detect replication slippage variants at "
            "microsatellite regions, and differentiate them as somatic or germline. "
            "Given paired tumor and normal sequence data, it builds a distribution "
            "for expected (normal) and observed (tumor) lengths of repeated sequence "
            "per microsatellite, and compares them using Pearson's Chi-Squared Test. "
            "Comprehensive testing indicates MSIsensor is an efficient and effective "
            "tool for deriving microsatellite instability (MSI) status from standard "
            "tumor-normal paired sequence data."
        ),
        dir="/home/danilovd/tools/msisensor/", #TODO
        commands={
            "scan": Command(
                key="scan",
                name="scan",
                description="scan homopolymers and miscrosatelites",
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
                    "Scanning reference genome"
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
                description="msi scoring",
                template=(
                    "./msisensor.linux msi "
                    "-d {microsatellite_list} "
                    "-n {normal_bam} "
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
                    "Loading BED regions",
                    "Loading BAM files",
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
            "MSIsensor-pro is an updated version of msisensor. MSIsensor-pro evaluates "
            "Microsatellite Instability (MSI) for cancer patients with next generation "
            "sequencing data. It accepts the whole genome sequencing, whole exome sequencing "
            "and target region (panel) sequencing data as input. MSIsensor-pro introduces a "
            "multinomial distribution model to quantify polymerase slippages for each tumor "
            "sample and a discriminative sites selection method to enable MSI detection "
            "without matched normal samples. For samples of various sequencing depths and "
            "tumor purities, MSIsensor-pro significantly outperformed the current leading "
            "methods which required matched normal samples in terms of both accuracy and "
            "computational cost."
        ),
        dir="/home/danilovd/tools/msisensor-pro/",
        commands={
            "scan": Command(
                key="scan",
                name="scan",
                description="scan homopolymers and miscrosatelites",
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
                    "Scanning reference genome"
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
                description="msi scoring",
                template=(
                    "./msisensor.linux msi "
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
                    "-0 {out_site_no_read_coverage} "
                ),
                steps=[
                    "Loading BED regions",
                    "Loading BAM files",
                    "Loading homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "reference_genome": None,
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
                    "out_site_no_read_coverage": 1,
                },
                optionals={
                    "reference_genome": "-g"
                },
            ),
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
            "two samples within the pair. Longer reads (ideally, 100 bp or longer) are recommended, "
            "as shorter reads are unlikely to entirely cover the microsatellite loci, and will be "
            "discarded after failing the quality control filters."
        ),
        dir="/home/danilovd/tools/MANTIS-1.0.5/",
        commands={
            "mantis": Command(
                key="mantis",
                name="mantis",
                description="Run MANTIS MSI analysis",
                template=(
                    "/home/danilovd/.conda/envs/mantis/bin/python ./mantis.py "
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
                    "--standard-deviations {standard_deviations}"
                ),
                steps=[
                    "Running MANTIS analysis",
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
    # "samtools": Tool(
    #     key="samtools",
    #     name="Samtools",
    #     description=(
    #         "Samtools is a set of utilities that manipulate alignments in the SAM (Sequence Alignment/Map)"
    #         ", BAM, and CRAM formats. It converts between the formats, does sorting, merging and indexing, "
    #         "and can retrieve reads in any regions swiftly."
    #     )
    # ),
}