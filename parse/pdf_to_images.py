#!/usr/bin/env python3old
import argparse
import os
import textwrap
from pathlib import Path

import rich
from util.pylib import log


def main():
    args = parse_args()
    log.started()

    pdf_to_images(args)

    msg = "You may now want to remove pages that do not contain useful traits."
    rich.print(f"\n[bold yellow]{msg}[/bold yellow]\n")

    log.finished()


def pdf_to_images(args):
    stem = args.in_pdf.stem
    dir_ = args.image_dir / stem
    dst = dir_ / f"{stem}"

    os.system(f"mkdir -p {dir_}")  # noqa: S605
    os.system(f"pdftocairo -jpeg {args.in_pdf} {dst}")  # noqa: S605


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
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
    main()
