from dataclasses import dataclass
from functools import reduce
from math import ceil
from operator import add
from typing import NamedTuple, Optional

import numpy as np
from osbpy import Osbject


class FrameData(NamedTuple):
    offset: int
    quadtree: "QuadNode"


@dataclass
class PixelData:
    alpha: float
    osb: Osbject


def calculate_mean(img: np.ndarray):
    return np.mean(img, axis=(0, 1), dtype=int)


def quad_split(image: np.ndarray):
    half_split = np.array_split(image, 2)
    res = map(lambda x: np.array_split(x, 2, axis=1), half_split)
    return reduce(add, res)


class QuadNode:
    tl: Optional["QuadNode"] = None
    tr: Optional["QuadNode"] = None
    bl: Optional["QuadNode"] = None
    br: Optional["QuadNode"] = None

    def __init__(
        self,
        image_pixels: np.ndarray,
        x: int,
        y: int,
        depth: int = 1,
        max_depth: int = 7,
    ):
        self._depth = depth
        self._max_depth = max_depth

        self.mean = calculate_mean(image_pixels)
        self.resolution = image_pixels.shape[:2]

        self.x = x
        self.y = y
        self.h = self.resolution[0] + 2
        self.w = self.resolution[1] + 2
        self.final = depth == max_depth or all(np.all(x == x[0]) for x in image_pixels)

        self.create_depth(image_pixels)

    def create_depth(self, image_pixels):
        if self.final:
            return
        split_img = quad_split(image_pixels)

        next_depth = self._depth + 1
        self.tl = type(self)(
            split_img[0],
            ceil(self.x - self.w / 4),
            ceil(self.y - self.h / 4),
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.tr = type(self)(
            split_img[1],
            ceil(self.x + self.w / 4),
            ceil(self.y - self.h / 4),
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.bl = type(self)(
            split_img[2],
            ceil(self.x - self.w / 4),
            ceil(self.y + self.h / 4),
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.br = type(self)(
            split_img[3],
            ceil(self.x + self.w / 4),
            ceil(self.y + self.h / 4),
            depth=next_depth,
            max_depth=self._max_depth,
        )
