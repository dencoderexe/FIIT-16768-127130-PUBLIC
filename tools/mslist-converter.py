import os
import argparse

def msisensor_scan_to_msisensor_pro_scan(site_file_msisensor: str, site_file_msisensor_pro: str) -> None:
    with open(site_file_msisensor, "r") as input, open(site_file_msisensor_pro, "w") as output:
        # skip msisensor header
        header = next(input, None)
        if header is None:
            print("Error: Microsatellite list file is empty")
            exit(1)

        # write msisensor-pro header
        output.write(
            "chromosome\t"
            "location\t"
            "repeat_unit_length\t"
            "repeat_times\t"
            "repeat_unit_bases\t"
            "left_flank_bases\t"
            "right_flank_bases\t"
            "threshold\t"
            "support_num\t"
            "filter\n"
        )
        
        for line in input:
            parts = line.strip().split("\t")
            # expect 10 columns (MSIsensor scan format)
            if len(parts) != 10:
                print("Error: Incorrect microsatellite list format, use MSIsensor scan to create one")
                exit(1)

            try:
                chromosome = parts[0]               # chromosome
                location = int(parts[1])            # start position (0-based)
                repeat_unit_length = int(parts[2])  # repeat unit length
                repeat_times = int(parts[4])        # number of repeats
                repeat_unit_bases = parts[7]        # repeat sequence (e.g. AC)
                left_flank_bases = parts[9]         # left flank sequence
                right_flank_bases = parts[9]        # right flank sequence

            except ValueError as e:
                print(f"Error: {e}")
                exit(1)

            output.write(
                f"{chromosome}\t{location}\t{repeat_unit_length}\t{repeat_times}\t{repeat_unit_bases}\t{left_flank_bases}\t{right_flank_bases}\t-1\t-1\tPASS\n"
            )

def msisensor_scan_to_repeatfinder(site_file_msisensor: str, bed_file_repeatfinder: str) -> None:
    # count matching bases between repeat unit and right flank
    # used to adjust end coordinate (RepeatFinder/MANTIS behavior)
    def repeat_right_flank_overlap(repeat_unit_bases: str, right_flank_bases: str) -> int:
        count = 0
        for x, y in zip(repeat_unit_bases, right_flank_bases):
            if x != y:
                break
            count += 1
        return count
    
    with open(site_file_msisensor, "r") as input, open(bed_file_repeatfinder, "w") as output:
        # skip msisensor header
        header = next(input, None)
        if header is None:
            print("Error: Microsatellite list file is empty")
            exit(1)
        
        for line in input:
            parts = line.strip().split("\t")
            # expect 10 columns (MSIsensor scan format)
            if len(parts) != 10:
                print("Error: Incorrect microsatellite list format, use MSIsensor scan to create one")
                exit(1)

            try:
                chromosome = parts[0]               # chromosome
                location = int(parts[1])            # start position (0-based)
                repeat_unit_length = int(parts[2])  # repeat unit length
                repeat_times = int(parts[4])        # number of repeats
                repeat_unit_bases = parts[7]        # repeat sequence (e.g. AC)
                right_flank_bases = parts[9]        # right flank sequence
            except ValueError as e:
                print(f"Error: {e}")
                exit(1)

            # compute overlap between repeat and right flank
            overlap = repeat_right_flank_overlap(repeat_unit_bases, right_flank_bases)

            # end = start + total repeat length + overlap
            end = location + (repeat_unit_length * repeat_times) + overlap

            # k-mer: (AC)12
            kmer = f"({repeat_unit_bases}){repeat_times}"

            # BED: chr, start, end, name, score, strand (unused)
            output.write(f"{chromosome}\t{location}\t{end}\t{kmer}\t0\t+\n")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert MSIsensor scan output to other formats."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_pro = subparsers.add_parser(
        "msisensor-pro",
        help="convert MSIsensor scan output to MSIsensor-pro scan format",
    )
    parser_pro.add_argument(
        "SITE_LIST",
        type=str,
        help="MSIsensor microsatellite list file",
    )
    parser_pro.add_argument(
        "OUTPUT",
        type=str,
        nargs="?",
        help="output file in MSIsensor-pro scan format",
    )

    parser_mantis = subparsers.add_parser(
        "mantis",
        help="convert MSIsensor scan output to RepeatFinder/MANTIS-compatible BED format",
    )
    parser_mantis.add_argument(
        "SITE_LIST",
        type=str,
        help="MSIsensor microsatellite list file",
    )
    parser_mantis.add_argument(
        "OUTPUT",
        type=str,
        nargs="?",
        help="output BED file",
    )

    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "msisensor-pro":
        output_file = args.OUTPUT
        if output_file is None:
            output_file = os.path.basename(args.SITE_LIST) + ".microsatellite.list.pro"

        msisensor_scan_to_msisensor_pro_scan(args.SITE_LIST, output_file)

    elif args.command == "mantis":
        output_file = args.OUTPUT
        if output_file is None:
            output_file = os.path.basename(args.SITE_LIST) + ".bed"

        msisensor_scan_to_repeatfinder(args.SITE_LIST, output_file)