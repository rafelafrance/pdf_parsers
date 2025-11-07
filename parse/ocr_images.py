#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path

import lmstudio as lms
from rich.console import Console

PROMPT = (
    "You are given images of text. "
    "I want you to extract all of the text in each image. "
    "Do not hallucinate."
)


def main(args: argparse.Namespace) -> None:
    image_paths = sorted(args.image_dir.glob("*.jpg"))

    console = Console(log_path=False)

    console.log("[blue]Started")

    with lms.Client(args.api_host) as client:
        model = client.llm.model(args.model_name)

        text = []

        for image_path in image_paths:
            console.log(f"[blue]{'=' * 80}")
            console.log(f"[blue]{image_path}")

            handle = client.files.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(PROMPT, images=[handle])

            try:
                results = model.respond(chat)
            except lms.LMStudioServerError as err:
                ocr_error = f"Server error: {err}"
                console.log(f"[red]{ocr_error}")
                text.append(ocr_error)
                continue

            text.append(results)
            console.log(f"[green]{results}")

    with args.ocr_text.open("w") as f:
        for results in text:
            f.write(str(results))
            f.write("\n")
            f.flush()

    console._log_render.omit_repeated_times = False
    console.log("[blue]Finished")


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        allow_abbrev=True,
        description=textwrap.dedent("""
            OCR a directory full of sliced images.
            """),
    )

    arg_parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Images of museum specimens are in this directory.""",
    )

    arg_parser.add_argument(
        "--ocr-text",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output OCRed text to this file.""",
    )

    arg_parser.add_argument(
        "--model-name",
        default="noctrex/Chandra-OCR-GGUF",
        help="""Use this language model. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--api-host",
        default="localhost:1234",
        help="""URL for the LM model. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
