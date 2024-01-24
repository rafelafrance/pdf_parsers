#!/usr/bin/env python3
import argparse
import json
import textwrap
from collections import defaultdict
from pathlib import Path

from PIL import Image
from pylib import image_transformer as trans
from pylib.ocr import image_to_string
from pylib.slice_box import Box
from tqdm import tqdm
from util.pylib import log


def main():
    args = parse_args()
    log.started()

    with args.in_json.open() as f:
        json_data = json.load(f)

    count = -1
    path = path_name(count, args.text_out)

    treatment = defaultdict(list)

    # OCR text boxes from the slice.py script
    for page in tqdm(json_data):
        if not page["boxes"]:
            continue

        image = Image.open(page["path"])
        if args.transform:
            image = trans.transform_label(args.transform, image)

        for box in page["boxes"]:
            box = Box(**box)

            cropped = image.crop((box.x0, box.y0, box.x1, box.y1))
            text = image_to_string(cropped)

            if box.start:
                path = path_name(count, args.text_out)

            treatment[str(path)].append(text)

    # Output text files
    for path, text in treatment.items():
        with Path(path).open("w") as f:
            f.write("\n".join(text))

    log.finished()


def path_name(count, text_out):
    count += 1
    stem = text_out.stem + f"_{str(count).zfill(3)}"
    path = text_out.with_stem(stem)
    return path


def parse_args():
    description = """Build text to prepare it for trait extraction."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        fromfile_prefix_chars="@",
    )

    arg_parser.add_argument(
        "--in-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""JSON file that holds the output of the slice.py
            (aka slice-gui) script.""",
    )

    arg_parser.add_argument(
        "--text-out",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Use this as a template for naming output text files. One per file per
            treatment. This script will add tie breakers to the file names to
            differentiate them.""",
    )

    transforms = list(trans.TRANSFORM_PIPELINES.keys())
    arg_parser.add_argument(
        "--transform",
        choices=transforms,
        help="""Transform images using the given pipeline in an attempt to improve OCR
            quality.""",
    )

    arg_parser.add_argument(
        "--conf",
        type=float,
        default=0.0,
        help="""Only keep OCR fragments that have a confidence >= to this. Set it to
            0.0 to get everything. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
