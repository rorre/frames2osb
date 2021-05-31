import os
import pickle

from osbpy import Osbject

from helper import PixelData, PixelValue, sort_datas

X_MAX = 640 // 10
Y_MAX = 480 // 10
OBJ_SCALE = 10
music_offset = 0
OBJ_OFFSET = OBJ_SCALE // 2


def generate_pixels(obj_size: int) -> PixelValue[Osbject]:
    "Generate pixels for storyboard, represented with a square every obj_size-px"
    if 640 % obj_size != 0 or 480 % obj_size != 0:
        raise Exception("obj_size is not a factor of 640 and 480.")

    x_max = 640 // obj_size
    y_max = 480 // obj_size
    obj_offset = obj_size // 2

    pixels: PixelValue[Osbject] = []
    for x in range(x_max):
        pixels.append([])
        for y in range(y_max):
            obj = Osbject(
                "dot.png",
                "Background",
                "Centre",
                -obj_offset + x * obj_size,
                obj_offset + y * obj_size,
            )
            obj.scale(0, -1, -1, 1, obj_size)
            pixels[x].append(obj)
    return pixels


def generate_osb(
    obj_size: int,
    output_filename,
    fps: int = 30,
    transparency_precision: int = 1,
):
    try:
        get_ipython()
        from tqdm.notebook import tqdm
    except NameError:
        from tqdm import tqdm

    data_files = os.listdir("datas")
    data_files.sort(key=sort_datas)
    pixels = generate_pixels(obj_size)

    # Prepare to save last alpha data before next data file is being loaded
    # This is because it is possible that next alpha data has the same alpha value as current one.
    # Therefore by remembering last alpha data we can avoid duplicate commands.
    # Also I know I can use list comprehension, but I'd rather have people be able to
    # read the code tbh.
    last_alpha_data: PixelValue[float] = []
    for x in range(X_MAX):
        last_alpha_data.append([])
        for y in range(Y_MAX):
            last_alpha_data[x].append(None)

    for data_file in tqdm(os.listdir("datas")):
        with open(os.path.join("datas", data_file), "rb") as f:
            pixel_data: PixelData = pickle.load(f)

        for x in range(X_MAX):
            for y in range(Y_MAX):
                for p in pixel_data[x][y]:
                    # offset here technically isn't offset in miliseconds, it is n-frame from start.
                    # So we use 1000 / fps.
                    start_offset = music_offset + p["offset"] * int(1000 / fps)
                    alpha = round(p["alpha"] / 255, transparency_precision)

                    # Only do another command if current alpha is different from last alpha.
                    # This is to avoid duplicate command and save more space.
                    if last_alpha_data[x][y] != alpha:
                        pixels[x][y].fade(0, start_offset, start_offset, alpha, alpha)
                        last_alpha_data[x][y] = alpha

        # Delete pixel data from memory to save memory because we don't use it anymore.
        del pixel_data

    Osbject.end(output_filename)
