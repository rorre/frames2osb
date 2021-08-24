from typing import List, NamedTuple, Optional, Tuple, TypeVar


class Point(NamedTuple):
    offset: int
    alpha: Optional[int] = None
    rgb: Optional[Tuple[int, int, int]] = None


T = TypeVar("T")
PixelData = List[List[List[Point]]]
PixelValue = List[List[T]]
