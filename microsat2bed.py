import os
import argparse

def microsat_list_to_bed(microsat_list_file: str, bed_file: str) -> None:
    def repeat_right_flank_overlap(repeat_unit_bases: str, right_flank_bases: str) -> int:
        count = 0
        for x, y in zip(repeat_unit_bases, right_flank_bases):
            if x != y:
                break
            count += 1
        return count
    
    with open(microsat_list_file, "r") as input, open(bed_file, "w") as output:
        header = next(input, None)
        if header is None:
            print("Error: Microsatellite list file is empty")
            exit(1)
        
        for line in input:
            parts = line.strip().split("\t")
            if len(parts) != 10:
                print("Error: Incorrect microsatellite list format, use MSIsensor scan to create one")
                exit(1)

            try:
                chr = parts[0]
                start = int(parts[1])
                repeat_unit_length = int(parts[2])
                repeat_times = int(parts[4])
                repeat_unit_bases = parts[7]
                right_flank_bases = parts[9]
            except ValueError as e:
                print(f"Error: {e}")
                exit(1)

            overlap = repeat_right_flank_overlap(repeat_unit_bases, right_flank_bases)

            end = start + (repeat_unit_length * repeat_times) + overlap
            kmer = f"({repeat_unit_bases}){repeat_times}"

            output.write(f"{chr}\t{start}\t{end}\t{kmer}\t0\t+\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "MICROSAT_LIST", 
        type=str, 
        help="microsatellite list file to convert to bed format"
    )
    parser.add_argument(
        "OUTPUT", 
        type=str,
        nargs="?",
        help="output BED file"
    )
    args = parser.parse_args()

    output_file = args.OUTPUT

    if output_file is None:
        output_file = os.path.basename(args.MICROSAT_LIST) + ".bed"

    microsat_list_to_bed(args.MICROSAT_LIST, output_file)