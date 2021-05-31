import argparse
import osb
import pixel_extract

parser = argparse.ArgumentParser(description="Generate storyboard for Bad Apple.")
parser.add_argument("outfile", help="Output .osb filename.")
parser.add_argument("size", help="Size of each square in storyboard.", type=int)
parser.add_argument(
    "-j",
    "--jobs",
    default=2,
    help="Number of threads to spawn.",
    metavar="N",
    type=int,
)
parser.add_argument(
    "--splits",
    default=16,
    help="Number of splits to generate.",
    metavar="N",
    type=int,
)
parser.add_argument(
    "--fps",
    default=30,
    help="FPS of the target storyboard.",
    metavar="N",
    type=int,
)
parser.add_argument(
    "--transparency",
    default=1,
    help="Transparency precision level.",
    metavar="N",
    type=int,
)
parser.add_argument(
    "--offset",
    default=1,
    help="Set storyboard offset.",
    metavar="N",
    type=int,
)
parser.add_argument(
    "--only-generate",
    action=argparse.BooleanOptionalAction,
    help="Only generate storyboard.",
)

if __name__ == "__main__":
    args = parser.parse_args()

    if not args.only_generate:
        print("> Extracting pixel data")
        pixel_extract.run(
            args.size,
            number_of_thread=args.jobs,
            number_of_splits=args.splits,
        )

    print("> Generating osb")
    osb.generate_osb(
        args.size,
        args.outfile,
        fps=args.fps,
        transparency_precision=args.transparency,
        music_offset=args.offset,
    )
