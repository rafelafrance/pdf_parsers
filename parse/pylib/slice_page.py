from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageTk
from pylib.slice_box import Box


@dataclass
class Page:
    path: Path = None
    width: int = None
    height: int = None
    photo: ImageTk = None
    boxes: list[Box] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "path": str(self.path),
            "boxes": [b.as_dict(self.height, self.photo.height()) for b in self.boxes],
        }

    def resize(self, canvas_height):
        if not self.photo:
            image = Image.open(self.path)
            image_width, image_height = image.size
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
    def load(cls, page_data: dict, canvas_height: int):
        page = cls(path=page_data["path"])
        page.resize(canvas_height)
        for box in page_data["boxes"]:
            box = Box(
                x0=box["x0"],
                y0=box["y0"],
                x1=box["x1"],
                y1=box["y1"],
                start=box["start"],
            )
            box.fit_to_canvas(page.height, canvas_height)
            page.boxes.append(box)
        return page
