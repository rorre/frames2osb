import os
import pickle
import shutil
from multiprocessing.pool import ThreadPool
from typing import TYPE_CHECKING, List

from PIL import Image

from helper import PixelData, Point, chunks, get_tqdm, sort_image_files

if TYPE_CHECKING:
    from tqdm import tqdm

all_image_files = os.listdir("frames")
all_image_files.sort(key=sort_image_files)


def process_frames(
    image_files: List[str],
    filename: str,
    obj_size: int,
    bar: "tqdm",
    start_frame: int = 0,
):
    if 640 % obj_size != 0 or 480 % obj_size != 0:
        raise Exception("obj_size is not a factor of 640 and 480.")

    x_max = 640 // obj_size
    y_max = 480 // obj_size

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

        gray = im_resized.convert("L")

        for x in range(x_max):
            for y in range(y_max):
                # Only add an entry if current alpha is different from last alpha.
                # Thus we only have timestamps where alpha value is different.
                current_alpha = int(gray.getpixel((x, y)))
                if not pixel_data[x][y] or pixel_data[x][y][-1].alpha != current_alpha:
                    pixel_data[x][y].append(Point(start_frame + i, current_alpha))

        # Delete from memory to save space.
        del im_resized
        del gray
        bar.update(1)

    # While using json is viable, pickle saves much more disk space and time.
    with open(filename, "wb") as f:
        pickle.dump(pixel_data, f)

    # Delete from memory to save space.
    del pixel_data


def run(obj_size, number_of_thread=2, number_of_splits=16):
    tqdm = get_tqdm()

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
                args=(
                    arr,
                    f"datas/data_{i}.dat",
                    obj_size,
                    pbar,
                    nchunk * i,
                ),
            )

        pool.close()
        pool.join()
