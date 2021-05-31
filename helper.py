import os
from typing import List, TypeVar, TypedDict


class Point(TypedDict):
    offset: int
    alpha: int


T = TypeVar("T")
PixelData = List[List[List[Point]]]
PixelValue = List[List[T]]


def sort_datas(filename):
    return int(os.path.splitext(filename)[0].split("_")[1])


def sort_image_files(f1: str) -> int:
    return int(os.path.splitext(f1)[0])


# https://stackoverflow.com/a/312464
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa


def get_tqdm():
    try:
        get_ipython()
        from tqdm.notebook import tqdm
    except NameError:
        from tqdm import tqdm

    return tqdm
