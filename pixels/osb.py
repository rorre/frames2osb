import os
import pickle
from typing import Tuple

from osbpy import Osbject

from helper import get_max_resolution, get_tqdm, sort_datas

from .types import PixelData, PixelValue


def generate_pixels(obj_size: int) -> PixelValue[Osbject]:
    "Generate pixels for storyboard, represented with a square every obj_size-px"
    x_max, y_max, x_shift = get_max_resolution(obj_size)
    obj_offset = obj_size // 2

    pixels: PixelValue[Osbject] = []
    for x in range(x_max):
        pixels.append([])
        for y in range(y_max):
            obj = Osbject(
                "res/dot.png",
                "Background",
                "Centre",
                -x_shift + obj_offset + x * obj_size,
                obj_offset + y * obj_size,
            )
            obj.scale(0, -1, -1, 1, obj_size)
            pixels[x].append(obj)
    return pixels


def _run_rgb(
    obj_size: int,
    output_filename,
    fps: int = 30,
    precision: int = 1,
    use_rgb: bool = False,
    music_offset: int = 0,
):
    tqdm = get_tqdm()

    data_files = os.listdir("datas")
    data_files.sort(key=sort_datas)
    pixels = generate_pixels(obj_size)
    x_max, y_max, _ = get_max_resolution(obj_size)

    last_pixel_data: PixelValue[Tuple[int, int, int]] = []
    for x in range(x_max):
        last_pixel_data.append([])
        for y in range(y_max):
            last_pixel_data[x].append(None)

    for data_file in tqdm(data_files):
        with open(os.path.join("datas", data_file), "rb") as f:
            pixel_data: PixelData = pickle.load(f)

        for x in range(x_max):
            for y in range(y_max):
                for p in pixel_data[x][y]:
                    # offset here technically isn't offset in miliseconds, it is n-frame from start.
                    # So we use 1000 / fps.
                    start_offset = music_offset + round(p.offset * 1000 / fps)

                    # TODO: Precision configurator
                    #       Maybe check if a pixel hasnt changed by like x values? idk

                    # Only do another command if current alpha is different from last alpha.
                    # This is to avoid duplicate command and save more space.
                    if last_pixel_data[x][y] != p.rgb:
                        pixels[x][y].colour(
                            0, start_offset, start_offset, *p.rgb, *p.rgb
                        )
                        last_pixel_data[x][y] = p.rgb

        # Delete pixel data from memory to save memory because we don't use it anymore.
        del pixel_data

    Osbject.end(output_filename)


def generate_osb(
    obj_size: int,
    output_filename,
    fps: int = 30,
    precision: int = 1,
    use_rgb: bool = False,
    music_offset: int = 0,
):
    if use_rgb:
        return _run_rgb(obj_size, output_filename, fps, precision, True, music_offset)
    tqdm = get_tqdm()

    data_files = os.listdir("datas")
    data_files.sort(key=sort_datas)
    pixels = generate_pixels(obj_size)
    x_max, y_max, _ = get_max_resolution(obj_size)

    # Prepare to save last alpha data before next data file is being loaded
    # This is because it is possible that next alpha data has the same alpha value as current one.
    # Therefore by remembering last alpha data we can avoid duplicate commands.
    # Also I know I can use list comprehension, but I'd rather have people be able to
    # read the code tbh.
    last_alpha_data: PixelValue[float] = []
    for x in range(x_max):
        last_alpha_data.append([])
        for y in range(y_max):
            last_alpha_data[x].append(None)

    for data_file in tqdm(data_files):
        with open(os.path.join("datas", data_file), "rb") as f:
            pixel_data: PixelData = pickle.load(f)

        for x in range(x_max):
            for y in range(y_max):
                for p in pixel_data[x][y]:
                    # offset here technically isn't offset in miliseconds, it is n-frame from start.
                    # So we use 1000 / fps.
                    start_offset = music_offset + round(p.offset * 1000 / fps)
                    alpha = round(p.alpha / 255, precision)

                    # Only do another command if current alpha is different from last alpha.
                    # This is to avoid duplicate command and save more space.
                    if last_alpha_data[x][y] != alpha:
                        pixels[x][y].fade(0, start_offset, start_offset, alpha, alpha)
                        last_alpha_data[x][y] = alpha

        # Delete pixel data from memory to save memory because we don't use it anymore.
        del pixel_data

    Osbject.end(output_filename)
