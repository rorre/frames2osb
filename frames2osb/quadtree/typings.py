from dataclasses import dataclass
from functools import reduce
from operator import add
from typing import List, NamedTuple, Optional, Union

import numpy as np
from numpy.typing import NDArray

from frames2osb.external.osbpy import Osbject

ImageArray = NDArray[np.int32]


class FrameData(NamedTuple):
    offset: int
    quadtree: "QuadNode"


@dataclass
class PixelData:
    rgb: int
    alpha: float
    osb: Osbject


# Code starting here are taken from
# https://medium.com/analytics-vidhya/transform-an-image-into-a-quadtree-39b3aa6e019a
# with quite a number of modification to fit my purpose.
def calculate_mean(img: ImageArray) -> Union[np.int32, ImageArray]:
    return np.mean(img, axis=(0, 1), dtype=np.int32)


def quad_split(image: ImageArray) -> List[ImageArray]:
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
        image_pixels: ImageArray,
        x: float,
        y: float,
        depth: int = 1,
        max_depth: int = 7,
    ):
        self._depth = depth
        self._max_depth = max_depth

        self.mean = calculate_mean(image_pixels)
        self.resolution = image_pixels.shape[:2]

        self.x = x
        self.y = y
        self.h = self.resolution[0]
        self.w = self.resolution[1]

        # We don't want the storyboard to be very very detailed so limit the max depth.
        # Max depth is 1-7.
        self.final = depth == max_depth or all(np.all(x == x[0]) for x in image_pixels)

        self.create_depth(image_pixels)

    def create_depth(self, image_pixels):
        if self.final:
            return
        split_img = quad_split(image_pixels)

        # Maybe trigonometry could help my ass here but I cba lol
        next_depth = self._depth + 1
        self.tl = type(self)(
            split_img[0],
            self.x - split_img[0].shape[1] / 2,
            self.y - split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.tr = type(self)(
            split_img[1],
            self.x + split_img[0].shape[1] / 2,
            self.y - split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.bl = type(self)(
            split_img[2],
            self.x - split_img[0].shape[1] / 2,
            self.y + split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.br = type(self)(
            split_img[3],
            self.x + split_img[0].shape[1] / 2,
            self.y + split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
