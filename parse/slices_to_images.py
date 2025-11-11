#!/usr/bin/env python3

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image

from parse.pylib.slice_box import Box


def main(args: argparse.Namespace) -> None:
    args.image_dir.mkdir(parents=True, exist_ok=True)

    with args.slices_json.open() as f:
        slices = json.load(f)

    subdir = 0

    for page in slices:
        image = Image.open(page["path"])

        for b, box in enumerate(page["boxes"], 1):
            box = Box(**box)

            box_slice = image.crop((box.x0, box.y0, box.x1, box.y1))
            page_path = Path(page["path"])

            if box.start:
                subdir += 1

            slice_path = args.image_dir

            if args.description_pattern:
                slice_path /= f"{args.description_pattern}_{subdir:03}"
                if box.start:
                    slice_path.mkdir(parents=True, exist_ok=True)

            slice_path /= f"{page_path.stem}_{b:02d}{page_path.suffix}"

            box_slice.save(slice_path)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Convert slices made with slice.py to images.
            The idea is that the slices have removed everything that is not part of
            the description, and you can OCR nice clean images.

            If the PDF document has descriptions for multiple taxa, you can add a
            pattern for subdirectories that will contain the slice images for each
            separate description. For instance if the PDF is for 2 new species of
            Anoplura you can add a "--description-pattern Anoplura", and at the start
            of each description a new directory of "Anoplura_001" and "Anoplura_002"
            will get created.
            """,
        ),
    )

    arg_parser.add_argument(
        "--slices-json",
        type=Path,
        required=True,
        metavar="PATH",
        help="""JSON file that holds the output of the slice.py
            (aka slice-gui) script.""",
    )

    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="""Where to place the images.""",
    )

    arg_parser.add_argument(
        "--description-pattern",
        metavar="PATTERN",
        help="""Put images for different descriptions into their own subdirectory
            using this pattern as the basis of subdirectory name.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
