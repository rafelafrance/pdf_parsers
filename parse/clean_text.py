#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

import rich
from tqdm import tqdm
from util.pylib import log, util

from parse.pylib.text_cleaner import MOJIBAKE, MOJIBAKE_WORDS


def main():
    log.started()

    args = parse_args()

    dirty = list(args.dirty_dir.glob("*.txt"))

    trans = str.maketrans(MOJIBAKE)

    for in_path in tqdm(dirty):
        clean(in_path, args.clean_dir, trans)

    msg = "You may want to look over and edit the output text."
    rich.print(f"\n[bold yellow]{msg}[/bold yellow]\n")

    log.finished()


def clean(in_path: Path, clean_dir: Path, trans):
    with in_path.open() as raw_file:
        text = raw_file.read()

    text = util.clean_text(text, trans=trans, replace=MOJIBAKE_WORDS)

    out_path = clean_dir / in_path.name
    with out_path.open("w") as clean_file:
        clean_file.write(text)


def parse_args():
    description = """Clean text to prepare it for trait extraction."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        fromfile_prefix_chars="@",
    )

    arg_parser.add_argument(
        "--dirty-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Get input text files from this directory.""",
    )

    arg_parser.add_argument(
        "--clean-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the cleaned text files to this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
