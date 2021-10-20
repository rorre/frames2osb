import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Literal, Optional, TypedDict, Union

FFPROBE_CMD = 'ffprobe -v quiet -print_format json -show_format -show_streams "{0}"'
FFMPEG_CMD = 'ffmpeg -i "{0}" frames/%03d.jpg'


# Minimum typing just to get it done
class Stream(TypedDict):
    index: int
    codec_type: Union[Literal["video"], Literal["audio"]]
    avg_frame_rate: str
    r_frame_rate: str
    duration: str
    bit_rate: str


class Format(TypedDict):
    filename: str
    nb_streams: int
    duration: str
    size: str
    bit_rate: str


class FFProbeResult(TypedDict):
    streams: List[Stream]
    format: Format


def get_stream(path: Path) -> Stream:
    result = subprocess.run(
        FFPROBE_CMD.format(path.absolute().as_posix()), capture_output=True
    )

    js_result: FFProbeResult = json.loads(result.stdout)
    if not js_result["format"]["nb_streams"]:
        raise Exception("Cannot find any stream in file!")

    video_stream: Optional[Stream] = None
    streams = js_result["streams"]
    for s in streams:
        if s["codec_type"] == "video":
            video_stream = s
            break

    if not video_stream:
        raise Exception("Cannot find any video stream in file!")

    return video_stream


def convert_video(video: str) -> float:
    p = Path(video)
    if not p.exists:
        raise FileNotFoundError(f"File {p} does not exist.")

    print("> Getting video stream from file")
    video_stream = get_stream(p)

    print("> Converting to frames")
    if Path("frames").exists():
        while True:
            ans = input(
                "Frames folder already exist, do you wish to replace it? [y/n] "
            )
            if ans.lower() == "y":
                break
            elif ans.lower() == "n":
                sys.exit(1)

    try:
        shutil.rmtree("frames")
    except FileNotFoundError:
        pass

    os.makedirs("frames", exist_ok=True)
    subprocess.run(FFMPEG_CMD.format(p.absolute().as_posix()), check=True)

    # I would've used literal_eval if it actually works with division lol
    fps: float = eval(video_stream["avg_frame_rate"])
    return fps
