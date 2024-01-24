from pathlib import Path

from PIL import Image, ImageTk
from pylib.slice_box import Box


class Page:
    def __init__(self, path: Path, canvas_height: int) -> None:
        self.path = path
        self.canvas_height = canvas_height
        self.photo = None
        self.image_height = None
        self.boxes = []
        self.resize(canvas_height)

    def as_dict(self) -> dict:
        return {
            "path": str(self.path),
            "boxes": [
                b.as_dict(self.image_height, self.canvas_height) for b in self.boxes
            ],
        }

    def resize(self, canvas_height):
        if not self.photo:
            image = Image.open(self.path)
            image_width, image_height = image.size
            self.image_height = image_height
            ratio = canvas_height / image_height
            new_width = int(image_width * ratio)
            new_height = int(image_height * ratio)
            resized = image.resize((new_width, new_height))
            self.photo = ImageTk.PhotoImage(resized)

    def filter(self, x=None, y=None):
        new = []
        for box in self.boxes:
            if x is not None and box.point_hit(x, y):
                continue
            if x is None and box.too_small():
                continue
            new.append(box)
        self.boxes = new

    def find(self, x, y) -> Box | None:
        for box in self.boxes:
            if box.point_hit(x, y):
                return box
        return None

    def all_box_ids(self) -> list[int]:
        return [b.id for b in self.boxes]

    @classmethod
    def load_json(cls, page_data: dict, canvas_height: int):
        page = cls(path=page_data["path"], canvas_height=canvas_height)
        page.resize(canvas_height)
        for box in page_data["boxes"]:
            box = Box(
                x0=box["x0"],
                y0=box["y0"],
                x1=box["x1"],
                y1=box["y1"],
                start=box["start"],
            )
            box.fit_to_canvas(page.image_height, canvas_height)
            page.boxes.append(box)
        return page
