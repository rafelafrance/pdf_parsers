#!/usr/bin/env python3
import argparse
import textwrap
from collections import defaultdict
from pathlib import Path

import regex as re
from tqdm import tqdm

from parse.pylib import sentence_pipeline
from parse.pylib.text_cleaner import make_sentences

CHOICES = ["shift-left", "taxon-lines", "split-treatments"]


def main():
    args = parse_args()

    match args.utility:
        case "shift-left":
            shift_left(args.in_xhtml, args.out_xhtml, args.pattern)

        case "taxon-lines":
            taxon_lines(args.in_text, args.pattern)

        case "split-treatments":
            split_treatments(args.in_text, args.out_dir, args.pattern)


def split_treatments(in_text: Path, out_dir: Path, pattern: str) -> None:
    sep_re = re.compile(rf"{pattern}")

    nlp = sentence_pipeline.pipeline()

    treatments = defaultdict(list)
    path = None
    i = 0

    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    with in_text.open() as fin:
        for ln in fin.readlines():
            if sep_re.search(ln):
                i += 1
                path = str(out_dir / f"{in_text.stem}_treatment_{i:04d}.txt")
            else:
                treatments[path].append(ln)

    for path, lines in tqdm(treatments.items()):
        path = Path(path)
        text = clean(nlp, lines)
        with path.open("w") as out:
            out.writelines(text)


def clean(nlp, lines: list[str]) -> str:
    text = " ".join(lines)
    text = " ".join(text.split())
    lines = make_sentences(nlp, text)
    text = "".join(lines)

    # Fix odd splits
    text = re.sub(r"([a-z])(-|–)\s([a-z])", r"\1\2", text, flags=re.IGNORECASE)
    text = re.sub(r"\n([,;:])", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"([,;:=])\n", r"\1 ", text, flags=re.IGNORECASE)
    text = re.sub(r"([a-z])\n([a-z])", r"\1 \2", text, flags=re.IGNORECASE)

    return text


def taxon_lines(in_text: Path, pattern: str):
    sep_re = re.compile(rf"{pattern}")
    found = False

    with in_text.open() as fin:
        for ln in fin.readlines():
            if sep_re.search(ln):
                found = True
            elif found:
                found = False
                print(ln.strip())


def shift_left(in_xhtml: Path, out_xhtml: Path, pattern: str, gap: int = 4) -> None:
    word_re = re.compile(rf"{pattern}")
    y_min_re = re.compile(r'yMin="[\d.]+"')
    x_min_re = re.compile(r'xMin="([\d.]+)"')
    x_max_re = re.compile(r'xMax="([\d.]+)"')

    y_min = "~~~???///"
    x_pos = 0.0

    with in_xhtml.open() as fin, out_xhtml.open("w") as out:
        for ln in fin.readlines():
            if word_re.search(ln):
                match = y_min_re.search(ln)
                y_min = match.group(0)
                x_max = x_max_re.search(ln)
                x_pos = float(x_max.group(1))

            elif ln.find(y_min) > -1:
                x_min = x_min_re.search(ln)
                x_min = float(x_min.group(1))

                x_max = x_max_re.search(ln)
                x_max = float(x_max.group(1))

                diff = x_max - x_min

                ln = x_min_re.sub(f'xMin="{x_pos + gap}"', ln)
                ln = x_max_re.sub(f'xMax="{x_pos + gap + diff}"', ln)

                x_pos = x_pos + gap + diff

            out.write(ln)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """
        These are utilities that try to fix various problems when extracting text from
        PDFs. The problems are particular to individual PDFs.

        - shift-left: Move words so they all fall into the same column. There is a PDF
          where they inserted spaces into the taxon name before the section name which
          causes the xhtml_to_text utility to interpret the line as 2 columns. This
          messes up the order of the text. This utility moves the text in the line so
          that gaps no longer trigger a new column. For example,
          "135i. Astragalus Linnaeus     sect. Tiopsidei Barneby, Mem. New ..."
          becomes
          "135i. Astragalus Linnaeus sect. Tiopsidei Barneby, Mem. New ...".

        - taxon-lines: I have a text file with each treatment separated by a line of
          equal signs (====...). Note that the treatments were separated manually while
          also removing excess non-treatments data. There are two issues I want to check
          before separating the treatments into separate files:
          1. Did I actually get all of the treatments?
          2. Are the treatment taxonomies at the right level? Some Unicode characters
             cause issues with line ordering.

        - split-treatments: After separating all treatments in a PDF with lines of
          equal signs (====...), write each treatment into a separate file.
        """
        ),
    )

    arg_parser.add_argument(
        "--utility",
        choices=CHOICES,
        required=True,
    )

    arg_parser.add_argument(
        "--in-text",
        type=Path,
        metavar="PATH",
        help="""Input text is in this file. It should be preprocessed and have
            separators between the treatments.""",
    )

    arg_parser.add_argument(
        "--in-xhtml",
        type=Path,
        metavar="PATH",
        help="""Input XHTML is in this file.""",
    )

    arg_parser.add_argument(
        "--out-xhtml",
        type=Path,
        metavar="PATH",
        help="""Output the XHTML to this file.""",
    )

    arg_parser.add_argument(
        "--out-dir",
        type=Path,
        metavar="PATH",
        help="""Output treatments to this directory.""",
    )

    arg_parser.add_argument(
        "--pattern",
        metavar="PATTERN",
        help="""A regular expression pattern with different uses for each utility.
            You will want to quote this argument.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
