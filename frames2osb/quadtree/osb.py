import os
import pickle
from typing import Dict, List, cast

from tqdm.auto import tqdm

from frames2osb.external.osbpy import Osbject
from frames2osb.helper import get_max_resolution, sort_datas
from frames2osb.quadtree.typings import FrameData, PixelData, QuadNode

USE_AMOGUS = False

pixels: Dict[str, PixelData] = {}
children_keys: Dict[str, List[str]] = {}


def disable_childs(key: str, offset: int):
    for k in children_keys[key]:
        if k in pixels and pixels[k].alpha != 0:
            pixels[k].osb.fade(0, offset, offset, 0, 0)
            pixels[k].alpha = 0
        disable_childs(k, offset)


def generate_particles(
    quality: int,
    frame: FrameData,
    fps: int = 30,
    precision: int = 1,
    use_rgb: bool = False,
    music_offset: int = 0,
    parent_key: str = "",
):
    _, _, x_shift = get_max_resolution(1)
    qtree: QuadNode = frame.quadtree
    start_offset = music_offset + round(frame.offset * 1000 / fps)

    # All this child thing is really bizarre, I know. I'll try to explain it:
    # Basically, for "key" here is a childrent of "parent_key".
    # By children, I mean it lives under "parent" pixels.
    # And so we store ourself to the list of our parent's children.
    #
    # Here is a good tree of it:
    #          vvvvvvvvvv               -----  vvvvvvvvv
    #         > Parent 1 <              |     > Child 4 <
    #          ^^^^^^^^^^               |      ^^^^^^^^^
    #              |                    |          |
    #        -----------------          |    -------------
    #        |   |   |       |          |    |   |   |   |
    #       ... ... ...   vvvvvvvvv     |   ... ... ... ...
    #                    > Child 4 < ---       (Repeats)
    #                     ^^^^^^^^^
    # With this relationship in mind, if we are a parent and we are turning on
    # our element, we can simply look at "children_keys" that we purpose as a
    # table and recursively disable all childs within it.
    key = "{0.x}:{0.y}:{0.w}:{0.h}".format(qtree)
    if parent_key and key not in children_keys[parent_key]:
        children_keys[parent_key].append(key)

    if key not in children_keys:
        children_keys[key] = []

    if qtree.final or qtree._depth == quality:
        # Recursively disable ALL childs (that means also disable child of child)
        disable_childs(key, start_offset)
        if key not in pixels:
            # Initialize if this is the first time we are in the storyboard.
            if USE_AMOGUS:
                pixels[key] = PixelData(
                    -1,
                    -1,
                    Osbject(
                        "res/amogus.png",
                        "Background",
                        "Centre",
                        qtree.x - x_shift,
                        qtree.y,
                        6,
                        68,
                        "LoopForever",
                    ),
                )
                pixels[key].osb.scale(0, 0, 0, 1, qtree.h / 1024)
            else:
                pixels[key] = PixelData(
                    -1,
                    -1,
                    Osbject(
                        "res/dot.png",
                        "Background",
                        "Centre",
                        qtree.x - x_shift,
                        qtree.y,
                    ),
                )
                pixels[key].osb.vecscale(0, 0, 0, 1, 1, qtree.w + 1, qtree.h + 1)
            pixels[key].osb.fade(0, 0, 0, 0, 0)

        if use_rgb:
            mean_rgb = cast(List[int], qtree.mean)

            minimum_delta = 0
            rgb_total = sum(mean_rgb)
            if abs(rgb_total - pixels[key].rgb) > minimum_delta:
                pixels[key].rgb = rgb_total
                pixels[key].osb.colour(
                    0, start_offset, start_offset, *mean_rgb, *mean_rgb
                )
            if pixels[key].alpha <= 0:
                pixels[key].osb.fade(0, start_offset, start_offset, 1, 1)
                pixels[key].alpha = 1
        else:
            mean_alpha = cast(int, qtree.mean)
            alpha = round(mean_alpha / 255, precision)

            if pixels[key].alpha != alpha:
                pixels[key].alpha = alpha
                pixels[key].osb.fade(0, start_offset, start_offset, alpha, alpha)
    else:
        # Disable ourselves if any of our child is turning on.
        if key in pixels and pixels[key].alpha != 0:
            pixels[key].osb.fade(0, start_offset, start_offset, 0, 0)
            pixels[key].alpha = 0

        for q in (qtree.tl, qtree.tr, qtree.bl, qtree.br):
            if q:
                generate_particles(
                    quality,
                    FrameData(frame.offset, q),
                    fps,
                    precision,
                    use_rgb,
                    music_offset,
                    key,
                )


def generate_osb(
    quality: int,
    output_filename: str,
    fps: int = 30,
    precision: int = 1,
    use_rgb: bool = False,
    music_offset: int = 0,
):
    data_files = os.listdir("datas")
    data_files.sort(key=sort_datas)

    for data_file in tqdm(data_files):
        with open(os.path.join("datas", data_file), "rb") as f:
            frame_data: List[FrameData] = pickle.load(f)

        for frame in frame_data:
            generate_particles(
                quality,
                frame,
                fps,
                precision,
                use_rgb,
                music_offset,
            )
            del frame
        del frame_data

    Osbject.end(output_filename)
