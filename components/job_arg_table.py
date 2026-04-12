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
        case "min_homo_size_dist":
            return "Min homopolymer size for distribution analysis"
        case "max_homo_size_dist":
            return "Max homopolymer size for distribution analysis"
        
        case "min_microsat_size":
            return "Min microsatellite size"
        case "min_microsat_size_dist":
            return "Min microsatellite size for distribution analysis"
        case "max_microsat_size_dist":
            return "Max microsatellite size for distribution analysis"
        
        case "span_size_window":
            return "Span size around window for extracting reads"
        
        case "homopolymer_only":
            return "Homopolymer only"
        case "microsatellite_only":
            return "Microsatellite only"
        
        case "include_zero_coverage_sites":
            return "Include zero coverage sites"
        case "out_site_no_read_coverage":
            return "Include sites with no read coverage"
        
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

        case _:
            return arg.replace("_", " ").capitalize()

def format_arg_value(arg: str, value) -> str:
    if value in (None, "", []):
        return "—"

    match arg:
        case ("homopolymer_only" | "microsatellite_only" | "coverage_normalization" | "write_index" |
                "include_zero_coverage_sites" | "include-zero-coverage-sites" | "out_site_no_read_coverage"):
            return "Yes" if value == 1 else "No"
        case ("reference_genome" | "microsatellite_list" | "tumor_bam" | "normal_bam" | "bam_file" | "bed_file"):
            return os.path.basename(value)
        case _:
            return value

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
    