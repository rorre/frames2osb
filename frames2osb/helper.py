import math
import os
import shutil
import sys
import warnings
from functools import cache
from typing import List, Tuple, TypeVar, Generic

from PIL import Image

T = TypeVar("T")


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
def chunks(lst: List[T], n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa


class SimpleProgressBar:
    def __init__(self, total: int):
        self.current = -1
        self.total = total
        self.print_progress()

    def print_progress(self):
        w, _ = shutil.get_terminal_size()
        bar_size = w - len("[] " + str(self.current) + "/" + str(self.total))

        only_number = False
        if bar_size < 0:
            only_number = True

        filled = math.floor(max(0, self.current) / self.total * bar_size)
        if only_number:
            sys.stdout.write(f"\r{self.current}/{self.total}")
        else:
            sys.stdout.write(
                f"\r[{'#' * filled}{' ' * (bar_size - filled)}] "
                + f"{self.current}/{self.total}"
            )
        sys.stdout.flush()

    def update(self, amount: int):
        self.current += amount
        self.print_progress()


class ListProgressBar(SimpleProgressBar, Generic[T]):
    def __init__(self, arr: List[T]):
        super().__init__(len(arr))
        self.arr = arr
        self.print_progress()

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        self.print_progress()
        if self.current < self.total:
            return self.arr[self.current]
        raise StopIteration
