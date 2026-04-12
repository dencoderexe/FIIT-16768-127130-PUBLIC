from models.jobs import Job

import os
import dash_mantine_components as dmc

def format_arg_name(arg: str) -> str:
    match arg:
        case "reference_genome":
            return "Reference genome"
        case "microsatellite_list":
            return "Microsatellite list"
        case "bam_file":
            return "BAM file"
        case "bam_files":
            return "BAM files"
        case "tumor_bam":
            return "Tumor BAM"
        case "normal_bam":
            return "Normal BAM"
        case "bed_file":
            return "BED file"
        case "model":
            return "Model"
        case "output":
            return "Output"
        case "save_next_to":
            return "Save next to"

        case "threads":
            return "Threads"
        case "region":
            return "Region"

        case "fdr_threshold":
            return "FDR threshold"
        case "instable_sites_threshold":
            return "Instable sites threshold"

        case "coverage":
            return "Coverage"
        case "coverage_normalization":
            return "Coverage normalization"

        case "min_homo_size":
            return "Min homopolymer size"
        case "max_homo_size":
            return "Max homopolymer size"
        case "min_homo_size_dist":
            return "Min homopolymer size for distribution analysis"
        case "max_homo_size_dist":
            return "Max homopolymer size for distribution analysis"

        case "min_microsat_size":
            return "Min microsatellite motif length"
        case "max_microsat_len":
            return "Max microsatellite motif length"
        case "min_microsat_rep":
            return "Min microsatellite repeats"
        case "min_microsat_size_dist":
            return "Min microsatellite motif length for distribution analysis"
        case "max_microsat_size_dist":
            return "Min microsatellite motif length for distribution analysis"

        case "context_len":
            return "Context length"
        case "span_size_window":
            return "Span size window"

        case "homopolymer_only":
            return "Homopolymer only"
        case "microsatellite_only":
            return "Microsatellite only"

        case "include_zero_coverage_sites":
            return "Include zero-coverage sites"

        # MANTIS
        case "min_read_quality":
            return "Min read quality"
        case "min_locus_quality":
            return "Min locus quality"
        case "min_read_length":
            return "Min read length"
        case "min_locus_coverage":
            return "Min locus coverage"
        case "min_repeat_reads":
            return "Min repeat reads"
        case "standard_deviations":
            return "Standard deviations"

        # RepeatFinder
        case "min_length":
            return "Min repeat region length"
        case "max_length":
            return "Max repeat region length"
        case "min_repeats":
            return "Min k-mer repeats"
        case "min_kmer":
            return "Min k-mer length (bp)"
        case "max_kmer":
            return "Max k-mer length (bp)"

        case "write_index":
            return "Write index"

        case _:
            return arg.replace("_", " ").replace("-", " ").capitalize()

def format_arg_value(arg: str, value) -> str:
    if value in (None, "", []):
        return "—"

    match arg:
        case (
            "homopolymer_only"
            | "microsatellite_only"
            | "coverage_normalization"
            | "write_index"
            | "include_zero_coverage_sites"
            | "out_site_no_read_coverage"
        ):
            return "Yes" if value == 1 else "No"

        case (
            "reference_genome"
            | "microsatellite_list"
            | "tumor_bam"
            | "normal_bam"
            | "bam_file"
            | "bed_file"
            | "model"
            | "save_next_to"
        ):
            return os.path.basename(value)

        case "bam_files":
            return ", ".join(os.path.basename(v) for v in value) if isinstance(value, list) else str(value)

        case _:
            return str(value)

def job_arg_table(job: Job) -> dmc.Table:
    return dmc.Table(
        highlightOnHover=True,
        withTableBorder=True,
        withColumnBorders=True,
        variant="vertical",
        children=[
            dmc.TableTbody([
                dmc.TableTr([
                    dmc.TableTh(format_arg_name(arg), w=160),
                    dmc.TableTd(format_arg_value(arg, value) if value is not None else "not selected"),
                ])
                for arg, value in sorted(
                    job.args.items(),
                    key=lambda x: (
                        x[0] not in ("tumor_bam", "normal_bam", "bed_file", "microsatellite_list", "model"),
                        x[0],
                    )
                )
                if arg not in ("output",)
            ])
        ],
    )
    