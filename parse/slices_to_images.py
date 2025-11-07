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

    for page in slices:
        image = Image.open(page["path"])

        for b, box in enumerate(page["boxes"], 1):
            box = Box(**box)

            cropped = image.crop((box.x0, box.y0, box.x1, box.y1))
            path = Path(page["path"])
            dst = args.image_dir / f"{path.stem}_{b:02d}{path.suffix}"

            cropped.save(dst)


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Convert slices made with slice.py to images.
            The idea is that the slices have removed everything that is not part of
            the description, and you can OCR nice clean images.
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

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
