#!/usr/bin/env python3
import argparse
import logging
import textwrap
from pathlib import Path

import rich
from util.pylib import log, util

from parse.pylib import sentence_pipeline
from parse.pylib.text_cleaner import MOJIBAKE, MOJIBAKE_WORDS, make_sentences


def main():
    args = parse_args()
    log.started()

    clean(args)

    msg = "You may want to look over and edit the output text."
    rich.print(f"\n[bold yellow]{msg}[/bold yellow]\n")

    log.finished()


def clean(args):
    with args.in_text.open() as raw_file:
        text = raw_file.read()

    # The bulk of the text cleaning happens in this function
    logging.info("Cleaning text")
    trans = str.maketrans(MOJIBAKE)
    text = util.clean_text(text, trans=trans, replace=MOJIBAKE_WORDS)

    # Break into sentences
    logging.info("Breaking text into sentences")
    nlp = sentence_pipeline.pipeline()
    nlp.max_length = args.nlp_max_length
    lines = make_sentences(text, args.nlp_max_length)

    with args.out_text.open("w") as clean_file:
        clean_file.writelines(lines)


def parse_args():
    description = """Clean text to prepare it for trait extraction."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        fromfile_prefix_chars="@",
    )

    arg_parser.add_argument(
        "--in-text",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Which text file to clean.""",
    )

    arg_parser.add_argument(
        "--out-text",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the cleaned text to this file.""",
    )

    arg_parser.add_argument(
        "--nlp-max-length",
        type=int,
        default=5,
        metavar="MB",
        help="""The maximum text file size to process. This is given in megabytes.
            This is a spaCy constraint. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    args.nlp_max_length *= 1_000_000
    return args


if __name__ == "__main__":
    main()
