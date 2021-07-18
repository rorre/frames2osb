from tap import Tap


class CLIParser(Tap):
    jobs: int = 2  # Number of threads to spawn.
    splits: int = 16  # Number of splits to generate.
    fps: int = 30  # Set storyboard's FPS.
    precision: int = 1  # Transparency precision level.
    offset: int = 1  # Set storyboard's offset.
    only_generate: bool = False  # Only generate storyboard.
    use_pixels: bool = False  # Generate each pixels instead of using QuadTree.
    use_rgb: bool = False  # Use RGB instead of alpha value.

    size: int
    outfile: str

    def configure(self):
        self.add_argument("outfile", help="Output .osb filename.")
        self.add_argument("size", help="Size of each square in storyboard.", type=int)
        self.description = "Generate storyboard for Bad Apple."


if __name__ == "__main__":
    args = CLIParser().parse_args()

    if args.use_pixels:
        from pixels import osb, pixel_extract
    else:
        from quadtree import osb, pixel_extract

    if not args.use_pixels and args.size >= 7:
        raise Exception("Can not use 7 or more for quadtree quality settings.")

    if not args.only_generate:
        print("> Extracting pixel data")
        pixel_extract.run(
            args.size,
            args.use_rgb,
            number_of_thread=args.jobs,
            number_of_splits=args.splits,
        )

    print("> Generating osb")
    osb.generate_osb(
        args.size,
        args.outfile,
        fps=args.fps,
        precision=args.precision,
        use_rgb=args.use_rgb,
        music_offset=args.offset,
    )
