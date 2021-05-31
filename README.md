# Bad Apple Storyboard

Storyboard generator for [this thing](https://osu.ppy.sh/beatmapsets/1478246#osu/3032686)

## Requirements
- Python 3.8
- Ffmpeg
- osbpy
- numpy
- Pillow
- tqdm

To install, simply do the following command:
```
pip install osbpy numpy pillow tqdm
```

## Generating
```
$ mkdir frames
$ ffmpeg -i badapple.mp4 -r 30 frames/%03d.jpg
$ python cli.py
```
or run `mp4osb.ipynb` in an IPython/Jupyter Notebook instance. (Much better with details)

## CLI Usage
```
usage: cli.py [-h] [-j N] [--splits N] [--fps N] [--transparency N] outfile size

Generate storyboard for Bad Apple.

positional arguments:
  outfile           Output .osb filename.
  size              Size of each square in storyboard.

optional arguments:
  -h, --help        show this help message and exit
  -j N, --jobs N    Number of threads to spawn.
  --splits N        Number of splits to generate.
  --fps N           FPS of the target storyboard.
  --transparency N  Transparency precision level.
  --only-generate, --no-only-generate
                    Only generate storyboard.
```