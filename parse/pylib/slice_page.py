from pathlib import Path
from typing import Literal

from PIL import Image, ImageTk

from parse.pylib.slice_box import Box

BoxSize = Literal["all", "largest", "smallest"]


class Page:
    def __init__(self, path: Path, canvas_height: int) -> None:
        self.path = path
        self.canvas_height = canvas_height
        self.photo = None
        self.image_height = -1
        self.boxes = []
        self.resize(canvas_height)

    def as_dict(self) -> dict:
        return {
            "path": str(self.path),
            "boxes": [
                b.as_dict(self.image_height, self.canvas_height) for b in self.boxes
            ],
        }

    def resize(self, canvas_height: int) -> None:
        if not self.photo:
            image = Image.open(self.path)
            image_width, image_height = image.size
            self.image_height = image_height
            ratio = canvas_height / image_height
            new_width = int(image_width * ratio)
            new_height = int(image_height * ratio)
            resized = image.resize((new_width, new_height))
            self.photo = ImageTk.PhotoImage(resized)

    def filter_delete(self, x: int, y: int) -> None:
        hit = self.find(x, y, "smallest")
        self.boxes = [b for b in self.boxes if b != hit]

    def filter_size(self) -> None:
        self.boxes = [b for b in self.boxes if not b.too_small()]

    def find(self, x: int, y: int, size: BoxSize = "all") -> Box | None:
        hits = [b for b in self.boxes if b.point_hit(x, y)]

        if hits:
            hits = sorted(hits, key=lambda b: b.area())
            return hits[-1] if size == "largest" else hits[0]

        return None

    @classmethod
    def load_json(cls, page_data: dict, canvas_height: int) -> "Page":
        page = cls(path=page_data["path"], canvas_height=canvas_height)
        page.resize(canvas_height)
        for box in page_data["boxes"]:
            box = Box(
                x0=box["x0"],
                y0=box["y0"],
                x1=box["x1"],
                y1=box["y1"],
                start=box["start"],
                clear=box["clear"],
            )
            box.fit_to_canvas(page.image_height, canvas_height)
            page.boxes.append(box)
        return page
