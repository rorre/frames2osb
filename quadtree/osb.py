import os
import pickle
from typing import Dict, List

from osbpy import Osbject

from helper import get_max_resolution, get_tqdm, sort_datas

from .types import FrameData, PixelData, QuadNode

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
    transparency_precision: int = 1,
    music_offset: int = 0,
    parent_key: str = "",
):
    _, _, x_shift = get_max_resolution(1)
    qtree: QuadNode = frame.quadtree
    start_offset = music_offset + round(frame.offset * 1000 / fps)
    key = "{0.x}:{0.y}:{0.w}:{0.h}".format(qtree)
    if parent_key and key not in children_keys[parent_key]:
        children_keys[parent_key].append(key)

    if key not in children_keys:
        children_keys[key] = []

    if qtree.final or qtree._depth == 7 - quality:
        disable_childs(key, start_offset)
        if key not in pixels:
            pixels[key] = PixelData(
                -1,
                Osbject(
                    "dot.png",
                    "Background",
                    "Centre",
                    qtree.x - x_shift,
                    qtree.y,
                ),
            )
            pixels[key].osb.vecscale(0, 0, 0, 1, 1, qtree.w + 1, qtree.h + 1)
            pixels[key].osb.fade(0, 0, 0, 0, 0)

        alpha = round(qtree.mean / 255, transparency_precision)
        if pixels[key].alpha == alpha:
            return

        pixels[key].alpha = alpha
        pixels[key].osb.fade(0, start_offset, start_offset, alpha, alpha)
    else:
        if key in pixels and pixels[key].alpha != 0:
            pixels[key].osb.fade(0, start_offset, start_offset, 0, 0)
            pixels[key].alpha = 0

        for q in (qtree.tl, qtree.tr, qtree.bl, qtree.br):
            generate_particles(
                FrameData(frame.offset, q),
                fps,
                transparency_precision,
                music_offset,
                key,
            )


def generate_osb(
    quality: int,
    output_filename: str,
    fps: int = 30,
    transparency_precision: int = 1,
    music_offset: int = 0,
):
    tqdm = get_tqdm()

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
                transparency_precision,
                music_offset,
            )
            del frame
        del frame_data

    Osbject.end(output_filename)
