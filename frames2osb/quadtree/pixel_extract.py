import traceback
import ujson
from multiprocessing import Pipe
from multiprocessing.connection import PipeConnection
import os
import pickle
import shutil
from multiprocessing.pool import AsyncResult, Pool
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
    pipe: PipeConnection,
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

        qtree = QuadNode.from_image(
            numpy_image, x_max // 2, y_max // 2, max_depth=max_depth
        )
        quad_frames.append(FrameData(start_frame + i, qtree))
        pipe.send(1)
        del im_resized

    output = [q.to_json() for q in quad_frames]
    with open(filename, "w") as f:
        ujson.dump(output, f)

    del quad_frames


def run(quality: int, use_rgb: bool = False, number_of_thread=2, number_of_splits=16):
    try:
        shutil.rmtree("datas")
    except FileNotFoundError:
        pass
    os.makedirs("datas", exist_ok=True)

    pbar = SimpleProgressBar(total=len(all_image_files))
    with Pool(number_of_thread) as pool:
        parent_conn, child_conn = Pipe()
        nchunk = len(all_image_files) // number_of_splits
        results: List[AsyncResult] = []
        for i, arr in enumerate(chunks(all_image_files, nchunk)):
            result = pool.apply_async(
                process_frames,
                args=(
                    arr,
                    f"datas/data_{i}.dat",
                    quality,
                    child_conn,
                    nchunk * i,
                    use_rgb,
                ),
                error_callback=lambda x: traceback.print_exception(x),
            )
            results.append(result)

        pool.close()
        while pbar.current < pbar.total - 1:
            parent_conn.recv()
            pbar.update(1)

        pool.join()
