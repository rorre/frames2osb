from dataclasses import dataclass
from functools import reduce
from operator import add
from typing import Any, List, NamedTuple, Optional, Union

import numpy as np
from numpy.typing import NDArray

from frames2osb.external.osbpy import Osbject

ImageArray = NDArray[np.int32]
MeanValue = np.signedinteger[Any] | NDArray[np.int32]


class FrameData(NamedTuple):
    offset: int
    quadtree: "QuadNode"

    def to_json(self):
        return {"offset": self.offset, "quadtree": self.quadtree.to_json()}

    @classmethod
    def from_json(cls, data: dict):
        return cls(data["offset"], QuadNode.from_json(data["quadtree"]))


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
        x: float,
        y: float,
        h: int,
        w: int,
        mean: MeanValue,
        final: bool = False,
        depth: int = 1,
        max_depth: int = 7,
    ):
        self._depth = depth
        self._max_depth = max_depth

        self.mean = mean
        self.resolution = [h, w]

        self.x = x
        self.y = y
        self.h = self.resolution[0]
        self.w = self.resolution[1]
        self.final = final

    @classmethod
    def from_image(
        cls,
        image: ImageArray,
        x: float,
        y: float,
        depth: int = 1,
        max_depth: int = 7,
    ):
        mean = calculate_mean(image)
        # We don't want the storyboard to be very very detailed so limit the max depth.
        # Max depth is 1-7.
        final = depth == max_depth or all(np.all(x == x[0]) for x in image)
        resolution = image.shape[:2]

        result = QuadNode(
            x, y, resolution[0], resolution[1], mean, final, depth, max_depth
        )
        result.create_depth(image)
        return result

    def to_json(self):
        return {
            "_depth": self._depth,
            "_max_depth": self._max_depth,
            "mean": self.mean.item()
            if isinstance(self.mean, np.signedinteger)
            else self.mean.tolist(),
            "resolution": self.resolution,
            "x": self.x,
            "y": self.y,
            "h": self.h,
            "w": self.w,
            "final": self.final,
            "tl": self.tl.to_json() if self.tl else None,
            "tr": self.tr.to_json() if self.tr else None,
            "bl": self.bl.to_json() if self.bl else None,
            "br": self.br.to_json() if self.br else None,
        }

    @classmethod
    def from_json(cls, data: dict):
        mean: MeanValue
        if isinstance(data["mean"], int):
            mean = np.int32(data["mean"])
        else:
            mean = np.array(data["mean"])

        self = QuadNode(
            data["x"],
            data["y"],
            data["h"],
            data["w"],
            mean,
            depth=data["_depth"],
            max_depth=data["_max_depth"],
        )

        self.tl = QuadNode.from_json(data["tl"]) if data["tl"] else None
        self.tr = QuadNode.from_json(data["tr"]) if data["tr"] else None
        self.bl = QuadNode.from_json(data["bl"]) if data["bl"] else None
        self.br = QuadNode.from_json(data["br"]) if data["br"] else None
        return self

    def create_depth(self, image_pixels):
        if self.final:
            return
        split_img = quad_split(image_pixels)

        # Maybe trigonometry could help my ass here but I cba lol
        next_depth = self._depth + 1
        self.tl = type(self).from_image(
            split_img[0],
            self.x - split_img[0].shape[1] / 2,
            self.y - split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.tr = type(self).from_image(
            split_img[1],
            self.x + split_img[0].shape[1] / 2,
            self.y - split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.bl = type(self).from_image(
            split_img[2],
            self.x - split_img[0].shape[1] / 2,
            self.y + split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
        self.br = type(self).from_image(
            split_img[3],
            self.x + split_img[0].shape[1] / 2,
            self.y + split_img[0].shape[0] / 2,
            depth=next_depth,
            max_depth=self._max_depth,
        )
