import os
import pickle
import shutil
from multiprocessing.pool import ThreadPool
from typing import List
from tqdm.auto import tqdm
from PIL import Image

from frames2osb.helper import chunks, get_max_resolution, sort_image_files
from frames2osb.pixels.typings import PixelData, Point


all_image_files = os.listdir("frames")
all_image_files.sort(key=sort_image_files)


def process_frames(
    image_files: List[str],
    filename: str,
    obj_size: int,
    bar: "tqdm",
    start_frame: int = 0,
    use_rgb: bool = False,
):
    x_max, y_max, _ = get_max_resolution(obj_size)

    # I know I can use list comprehension, but I'd rather have people be able to
    # read the code tbh.
    pixel_data: PixelData = []
    for x in range(x_max):
        pixel_data.append([])
        for y in range(y_max):
            pixel_data[x].append([])

    for i in range(len(image_files)):
        image_file = image_files[i]
        with Image.open(os.path.join("frames", image_file)) as im:
            im_resized = im.resize((x_max, y_max))

        if use_rgb:
            image = im_resized
        else:
            image = im_resized.convert("L")

        for x in range(x_max):
            for y in range(y_max):
                px = pixel_data[x][y]

                # Only add an entry if current value is different from last value.
                # Thus we only have timestamps where the values are different.
                if use_rgb:
                    current_rgb = image.getpixel((x, y))
                    if not px or px[-1].rgb != current_rgb:
                        pixel_data[x][y].append(
                            Point(offset=start_frame + i, rgb=current_rgb)
                        )
                else:
                    current_alpha = int(image.getpixel((x, y)))
                    if not px or px[-1].alpha != current_alpha:
                        pixel_data[x][y].append(
                            Point(offset=start_frame + i, alpha=current_alpha)
                        )

        # Delete from memory to save space.
        del im_resized
        del image
        bar.update(1)

    # While using json is viable, pickle saves much more disk space and time.
    with open(filename, "wb") as f:
        pickle.dump(pixel_data, f)

    # Delete from memory to save space.
    del pixel_data


def run(obj_size, use_rgb: bool = False, number_of_thread=2, number_of_splits=16):
    try:
        shutil.rmtree("datas")
    except FileNotFoundError:
        pass
    os.makedirs("datas", exist_ok=True)
    with ThreadPool(number_of_thread) as pool, tqdm(total=len(all_image_files)) as pbar:
        nchunk = len(all_image_files) // number_of_splits
        for i, arr in enumerate(chunks(all_image_files, nchunk)):
            pool.apply_async(
                process_frames,
                args=(arr, f"datas/data_{i}.dat", obj_size, pbar, nchunk * i, use_rgb),
            )

        pool.close()
        pool.join()
