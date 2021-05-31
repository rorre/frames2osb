import argparse
import osb
import pixel_extract

parser = argparse.ArgumentParser(description="Generate storyboard for Bad Apple.")
parser.add_argument("outfile", help="Output .osb filename.")
parser.add_argument("size", help="Size of each square in storyboard.")
parser.add_argument(
    "-j",
    "--jobs",
    default=2,
    help="Number of threads to spawn.",
    metavar="N",
)
parser.add_argument(
    "--splits",
    default=16,
    help="Number of splits to generate.",
    metavar="N",
)
parser.add_argument(
    "--fps",
    default=30,
    help="FPS of the target storyboard.",
    metavar="N",
)
parser.add_argument(
    "--transparency",
    default=1,
    help="Transparency precision level.",
    metavar="N",
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
            args.obj_size,
            number_of_thread=args.jobs,
            number_of_splits=args.splits,
        )

    print("> Generating osb")
    osb.generate_osb(
        args.obj_size,
        args.output_filename,
        fps=args.fps,
        transparency_precision=args.transparency,
    )
