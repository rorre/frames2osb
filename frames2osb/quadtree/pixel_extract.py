import os
import pickle
import shutil
from multiprocessing.pool import ThreadPool
from typing import List

import numpy as np
from PIL import Image

from frames2osb.helper import (
    SimpleProgressBar,
    chunks,
    get_max_resolution,
    sort_image_files,
)
from frames2osb.quadtree.typings import FrameData, QuadNode

all_image_files = os.listdir("frames")
all_image_files.sort(key=sort_image_files)


def process_frames(
    image_files: List[str],
    filename: str,
    quality: int,
    bar: SimpleProgressBar,
    start_frame: int = 0,
    use_rgb: bool = False,
):
    x_max, y_max, _ = get_max_resolution(1)
    max_depth = quality

    quad_frames: List[FrameData] = []
    for i in range(len(image_files)):
        image_file = image_files[i]
        with Image.open(os.path.join("frames", image_file)) as im:
            im_resized = im.resize((x_max, y_max))

        if use_rgb:
            numpy_image = np.array(im_resized)
        else:
            numpy_image = np.array(im_resized.convert("L"))

        qtree = QuadNode(numpy_image, x_max // 2, y_max // 2, max_depth=max_depth)
        quad_frames.append(FrameData(start_frame + i, qtree))
        bar.update(1)
        del im_resized

    with open(filename, "wb") as f:
        pickle.dump(quad_frames, f)

    del quad_frames


def run(quality: int, use_rgb: bool = False, number_of_thread=2, number_of_splits=16):
    try:
        shutil.rmtree("datas")
    except FileNotFoundError:
        pass
    os.makedirs("datas", exist_ok=True)

    pbar = SimpleProgressBar(total=len(all_image_files))
    with ThreadPool(number_of_thread) as pool:
        nchunk = len(all_image_files) // number_of_splits
        for i, arr in enumerate(chunks(all_image_files, nchunk)):
            pool.apply_async(
                process_frames,
                args=(arr, f"datas/data_{i}.dat", quality, pbar, nchunk * i, use_rgb),
            )

        pool.close()
        pool.join()
