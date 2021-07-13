from collections import namedtuple
from typing import List, TypeVar

Point = namedtuple("Point", ["offset", "alpha"])


T = TypeVar("T")
PixelData = List[List[List[Point]]]
PixelValue = List[List[T]]
