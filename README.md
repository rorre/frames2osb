# Bad Apple Storyboard

Storyboard generator for [this thing](https://osu.ppy.sh/beatmapsets/1478246#osu/3032686)

## Requirements
- Python 3.8
- Ffmpeg
- osbpy
- Pillow
- tqdm
- tap (if CLI)

To install, simply do the following command:
```
pip install osbpy pillow tqdm
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
usage: cli.py [--jobs JOBS] [--splits SPLITS] [--fps FPS] [--transparency TRANSPARENCY] [--offset OFFSET] [--only_generate] [--use_pixels]
              [-h]
              size outfile

Generate storyboard for Bad Apple.

positional arguments:
  size                  Size of each square in storyboard.
  outfile               Output .osb filename.

optional arguments:
  --jobs JOBS           (int, default=2) Number of threads to spawn.
  --splits SPLITS       (int, default=16) Number of splits to generate.
  --fps FPS             (int, default=30) Set storyboard's FPS.
  --transparency TRANSPARENCY
                        (int, default=1) Transparency precision level.
  --offset OFFSET       (int, default=1) Set storyboard's offset.
  --only_generate       (bool, default=False) Only generate storyboard.
  --use_pixels          (bool, default=False) Generate each pixels instead of using QuadTree.
  -h, --help            show this help message and exit
```

## RGB?
Soon, I guess.