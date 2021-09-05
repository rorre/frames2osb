# Frames2Osb

Converts frames (or video) to osu!storyboard. It is also the storyboard generator for [this thing](https://osu.ppy.sh/beatmapsets/1478246#osu/3032686).

## Requirements

-   Python 3.8
-   Ffmpeg
-   Pillow
-   numpy
-   typed-argument-parser

To install, simply do the following command:

```
poetry install
```

## Generating

```
$ frames2osb
```

## CLI Usage

```
usage: frames2osb [--video VIDEO] [-h] {pixels,quadtree} ...

positional arguments:
  {pixels,quadtree}
    pixels           Generate storyboard using pixel by pixel.
    quadtree         Generate storybord using quadtree.

optional arguments:
  --video VIDEO      (Optional[str], default=None)
  -h, --help         show this help message and exit
```

### Pixels

```
usage: frames2osb pixels [--jobs JOBS] [--splits SPLITS] [--fps FPS] [--precision PRECISION] [--offset OFFSET] [--only_generate] [--use_rgb]
                         [-h]
                         size outfile

Generate storyboard using pixels method.

positional arguments:
  size                  Size of each square in storyboard.
  outfile               Output .osb filename.

optional arguments:
  --jobs JOBS           (int, default=2) Number of threads to spawn.
  --splits SPLITS       (int, default=16) Number of splits to generate.
  --fps FPS             (int, default=30) Set storyboard's FPS.
  --precision PRECISION
                        (int, default=1) Transparency precision level.
  --offset OFFSET       (int, default=1) Set storyboard's offset.
  --only_generate       (bool, default=False) Only generate storyboard.
  --use_rgb             (bool, default=False) Use RGB instead of alpha value.
  -h, --help            show this help message and exit
```

### Quadtree

```
usage: frames2osb quadtree [--jobs JOBS] [--splits SPLITS] [--fps FPS] [--precision PRECISION] [--offset OFFSET] [--only_generate]
                           [--use_rgb] [-h]
                           {1..8} outfile

positional arguments:
  {1..8}                Numbers of depth in QuadTree function.
  outfile               Output .osb filename.

optional arguments:
  --jobs JOBS           (int, default=2) Number of threads to spawn.
  --splits SPLITS       (int, default=16) Number of splits to generate.
  --fps FPS             (int, default=30) Set storyboard's FPS.
  --precision PRECISION
                        (int, default=1) Transparency precision level.
  --offset OFFSET       (int, default=1) Set storyboard's offset.
  --only_generate       (bool, default=False) Only generate storyboard.
  --use_rgb             (bool, default=False) Use RGB instead of alpha value.
  -h, --help            show this help message and exit
```
