from typing import TYPE_CHECKING, Literal, Optional, cast
from tap import Tap
import argparse


class QualityAction(argparse.Action):
    def __call__(  # type: ignore
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: int,
        option_string: Optional[str] = None,
    ):
        if not 1 <= values <= 8:
            raise argparse.ArgumentError(
                self, "Quality must be between 1 and 8 (inclusive)"
            )
        setattr(namespace, self.dest, values)


class CommonParser(Tap):
    jobs: int = 2  # Number of threads to spawn.
    splits: int = 16  # Number of splits to generate.
    fps: int = 30  # Set storyboard's FPS.
    precision: int = 1  # Transparency precision level.
    offset: int = 1  # Set storyboard's offset.
    only_generate: bool = False  # Only generate storyboard.
    use_rgb: bool = False  # Use RGB instead of alpha value.
    outfile: str

    def configure(self) -> None:
        self.add_argument("outfile", help="Output .osb filename.")


class PixelParser(CommonParser):
    size: int

    def configure(self):
        super().configure()
        self.add_argument("size", help="Size of each square in storyboard.", type=int)
        self.description = "Generate storyboard using pixels method."


class QuadTreeParser(CommonParser):
    quality: int

    def configure(self) -> None:
        super().configure()
        self.add_argument(
            "quality",
            help="Numbers of depth in QuadTree function.",
            action=QualityAction,
            metavar="{1..8}",
        )


class CLIParser(Tap):
    if TYPE_CHECKING:
        method: Literal["pixels", "quadtree"]

    def configure(self) -> None:
        self.add_subparsers(help="sub-command help", dest="method")
        self.add_subparser("pixels", PixelParser)
        self.add_subparser("quadtree", QuadTreeParser)


def pixels(orig_args: CLIParser):
    from frames2osb.pixels import osb, pixel_extract

    args = cast(PixelParser, orig_args)
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


def quadtree(orig_args: CLIParser):
    from frames2osb.quadtree import osb, pixel_extract

    args = cast(QuadTreeParser, orig_args)
    if not args.only_generate:
        print("> Extracting pixel data")
        pixel_extract.run(
            args.quality,
            args.use_rgb,
            number_of_thread=args.jobs,
            number_of_splits=args.splits,
        )

    print("> Generating osb")
    osb.generate_osb(
        args.quality,
        args.outfile,
        fps=args.fps,
        precision=args.precision,
        use_rgb=args.use_rgb,
        music_offset=args.offset,
    )


def main():
    args = CLIParser().parse_args()

    if args.method == "pixels":
        pixels(args)
    else:
        quadtree(args)
