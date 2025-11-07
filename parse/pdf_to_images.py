#!/usr/bin/env python3

import argparse
import os
import textwrap
from pathlib import Path

import rich
from pylib import log


def main(args: argparse.Namespace) -> None:
    log.started()

    pdf_to_images(args.in_pdf, args.image_dir)

    msg = "You may now want to remove pages that do not contain useful traits."
    rich.print(f"\n[bold yellow]{msg}[/bold yellow]\n")

    log.finished()


def pdf_to_images(in_pdf: Path, image_dir: Path) -> None:
    stem = in_pdf.stem
    dir_ = image_dir / stem
    dst = dir_ / f"{stem}"

    os.system(f"mkdir -p {dir_}")  # noqa: S605
    os.system(f"pdftocairo -jpeg {in_pdf} {dst}")  # noqa: S605


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent(
            """
            Convert a PDF file to images (jpg) of pages (one image per page).
            Note: This will create a subdirectory under the given image directory
            with a name that matches the PDF file name.
            """,
        ),
    )

    arg_parser.add_argument(
        "--in-pdf",
        type=Path,
        required=True,
        metavar="PDF",
        help="""Which pdf file to convert to images.""",
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
