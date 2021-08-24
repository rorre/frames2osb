from typing import List, Optional, Tuple, TypeVar, NamedTuple


class Point(NamedTuple):
    offset: int
    alpha: Optional[int] = None
    rgb: Optional[Tuple[int, int, int]] = None


T = TypeVar("T")
PixelData = List[List[List[Point]]]
PixelValue = List[List[T]]
