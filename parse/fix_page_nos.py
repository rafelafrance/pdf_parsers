#!/usr/bin/env python3
import argparse
import shutil
import textwrap
from pathlib import Path

import rich
from pylib import log


def main(args: argparse.Namespace) -> None:
    log.started()

    paths = sorted(args.image_dir.glob(args.glob))
    for src in paths:
        parts = src.stem.split("_")
        if len(parts) != 2:  # noqa: PLR2004
            continue
        try:
            _ = int(parts[1])
            stem = f"{parts[0]}_{parts[1].zfill(4)}"
            dst = src.with_stem(stem)
            shutil.move(src, dst)
        except ValueError:
            rich.print(f"Could not rename: [bold red]{src}[/bold red]")
            continue

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent("""Fix image page numbers."""),
    )

    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="DIR",
        help="""The directory with messed up numbering.""",
    )

    arg_parser.add_argument(
        "--glob",
        default="*.jpg",
        help="""What files to change. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
