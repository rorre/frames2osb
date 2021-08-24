import math
import os
from typing import TYPE_CHECKING, List, Tuple
import warnings
from functools import cache

from PIL import Image

if TYPE_CHECKING:
    from IPython import get_ipython
    from tqdm import tqdm


def sort_datas(filename: str) -> int:
    return int(os.path.splitext(filename)[0].split("_")[1])


def sort_image_files(f1: str) -> int:
    return int(os.path.splitext(f1)[0])


@cache
def get_max_resolution(obj_size: int) -> Tuple[int, int, int]:
    im_file = os.listdir("frames")[0]
    with Image.open(os.path.join("frames", im_file)) as im:
        x_original, y_original = im.size

    osb_scale = y_original / 480
    scaled_x = math.ceil(x_original / osb_scale)
    if scaled_x % obj_size != 0 or 480 % obj_size != 0:
        warnings.warn(f"obj_size is not a factor of {scaled_x} and 480.")

    x_max = math.ceil(scaled_x / obj_size)
    y_max = 480 // obj_size
    x_shift = (scaled_x - 640) // 2

    return x_max, y_max, x_shift


# https://stackoverflow.com/a/312464
def chunks(lst: List, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa


def get_tqdm() -> "tqdm":
    try:
        get_ipython()
        from tqdm.notebook import tqdm
    except NameError:
        from tqdm import tqdm

    return tqdm
