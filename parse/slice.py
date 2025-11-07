#!/usr/bin/env python3
import json
import tkinter as tk
from itertools import cycle
from pathlib import Path
from tkinter import Event, filedialog, messagebox, ttk
from typing import ClassVar, LiteralString

from parse.pylib.slice_box import Box
from parse.pylib.slice_page import Page

FONT = ("DejaVu Sans", 24)
FONT_SM = ("DejaVu Sans", 16)
FONT_SM_I = ("DejaVu Sans", 16, "italic")
FONT_SM_U = ("DejaVu Sans", 16, "underline")
FONT_SM_UI = ("DejaVu Sans", 16, "underline italic")


class App(tk.Tk):
    row_span: ClassVar[int] = 10
    color_list: ClassVar[list[LiteralString]] = [
        "red",
        "blue",
        "green",
        "black",
        "purple",
        "orange",
        "cyan",
        "olive",
        "gray",
        "pink",
    ]

    def __init__(self) -> None:
        super().__init__()

        self.curr_dir = "."
        self.image_dir: Path = Path()
        self.canvas: tk.Canvas = tk.Canvas()
        self.pages = []
        self.colors = cycle(self.color_list)
        self.dirty = False
        self.dragging = False

        self.title("Slice images for OCR")

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.image_frame = ttk.Frame(master=self)
        self.image_frame.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.image_button = tk.Button(
            master=self, text="Choose image directory", command=self.get_image_dir
        )
        self.image_button.grid(row=0, column=1, padx=16, pady=16)

        self.load_button = tk.Button(master=self, text="Load", command=self.load)
        self.load_button.grid(row=1, column=1, padx=16, pady=16)

        self.save_button = tk.Button(
            master=self, text="Save", command=self.save, state="disabled"
        )
        self.save_button.grid(row=2, column=1, padx=16, pady=16)

        self.page_no = tk.IntVar()
        self.spinner = ttk.Spinbox(
            textvariable=self.page_no,
            wrap=True,
            font=FONT_SM,
            justify="center",
            state="disabled",
            command=self.display_page,
        )
        self.spinner.grid(row=3, column=1, padx=16, pady=16)

        self.action = tk.StringVar()
        self.action.set("add")
        self.radio_add = ttk.Radiobutton(
            master=self, variable=self.action, text="add", value="add"
        )
        self.radio_del = ttk.Radiobutton(
            master=self, variable=self.action, text="delete", value="delete"
        )
        self.radio_clear = ttk.Radiobutton(
            master=self, variable=self.action, text="clear area", value="clear"
        )
        self.radio_treatment = ttk.Radiobutton(
            master=self, variable=self.action, text="treatment start", value="start"
        )
        self.radio_add.grid(row=4, column=1, padx=16, pady=16)
        self.radio_del.grid(row=5, column=1, padx=16, pady=16)
        self.radio_clear.grid(row=6, column=1, padx=16, pady=16)
        self.radio_treatment.grid(row=7, column=1, padx=16, pady=16)

        self.protocol("WM_DELETE_WINDOW", self.safe_quit)

    @property
    def page(self) -> Page:
        return self.pages[self.page_no.get() - 1]

    def display_page(self) -> None:
        canvas_height = self.image_frame.winfo_height()
        self.page.resize(canvas_height)
        self.canvas.delete("all")
        self.canvas.create_image((0, 0), image=self.page.photo, anchor="nw")
        self.display_page_boxes()
        self.action.set("add")

    def display_page_boxes(self) -> None:
        self.clear_page_boxes()
        self.colors = cycle(self.color_list)
        for box in self.page.boxes:
            color = next(self.colors)
            dash = (30, 20) if box.start else ()
            fill = "#ccc" if box.clear else ""
            stipple = "gray50" if box.clear else ""
            self.canvas.create_rectangle(
                box.x0,
                box.y0,
                box.x1,
                box.y1,
                outline=color,
                fill=fill,
                width=4,
                dash=dash,
                stipple=stipple,
            )

    def clear_page_boxes(self) -> None:
        for i, id_ in enumerate(self.canvas.find_all()):
            if i:  # First object is the page itself
                self.canvas.delete(id_)

    def on_canvas_press(self, event: Event) -> None:
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.pages and self.action.get() == "add":
            self.dirty = True
            color = next(self.colors)
            id_ = self.canvas.create_rectangle(0, 0, 1, 1, outline=color, width=4)
            self.page.boxes.append(Box(id=id_, x0=x, y0=y, x1=x, y1=y))
            self.dragging = True
        elif self.pages and self.action.get() == "delete":
            self.dirty = True
            self.page.filter_delete(x, y)
            self.display_page_boxes()
            self.action.set("add")
        elif self.pages and self.action.get() == "clear":
            self.dirty = True
            box = self.page.find(x, y, "smallest")
            if box:
                box.clear = not box.clear
                self.display_page_boxes()
        elif self.pages and self.action.get() == "start":
            self.dirty = True
            box = self.page.find(x, y, "largest")
            if box:
                box.start = not box.start
                self.display_page_boxes()

    def on_canvas_move(self, event: Event) -> None:
        if self.dragging and self.pages and self.action.get() == "add":
            box = self.page.boxes[-1]
            box.x1 = self.canvas.canvasx(event.x)
            box.y1 = self.canvas.canvasy(event.y)
            self.canvas.coords(box.id, box.x0, box.y0, box.x1, box.y1)

    def on_canvas_release(self, _: Event) -> None:
        if self.dragging and self.pages and self.action.get() == "add":
            self.page.filter_size()
            self.display_page_boxes()
            self.dragging = False

    def save(self) -> None:
        if not self.pages:
            return

        path = filedialog.asksaveasfilename(
            initialdir=self.curr_dir,
            title="Save image boxes",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )

        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent
        self.dirty = False

        output = [p.as_dict() for p in self.pages]

        with path.open("w") as out_json:
            json.dump(output, out_json, indent=4)

    def load(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=self.curr_dir,
            title="Load image boxes",
            filetypes=(("json", "*.json"), ("all files", "*")),
        )
        if not path:
            return

        path = Path(path)
        self.curr_dir = path.parent

        if self.canvas is None:
            self.setup_canvas()
        canvas_height = self.image_frame.winfo_height()

        with path.open() as in_json:
            json_pages = json.load(in_json)

        self.dirty = False
        self.pages = []
        try:
            for page_data in json_pages:
                page = Page.load_json(page_data, canvas_height)
                self.pages.append(page)

            self.spinner_update(len(self.pages))
            self.save_button.configure(state="normal")
            self.display_page()

        except KeyError:
            messagebox.showerror(
                title="Load error",
                message="Could not load the JSON file",
            )
            self.pages = []
            self.save_button.configure(state="disabled")
            self.spinner_clear()
            self.canvas.delete("all")

    def setup_canvas(self) -> None:
        self.update()

        self.canvas = tk.Canvas(
            master=self.image_frame,
            width=self.image_frame.winfo_width(),
            height=self.image_frame.winfo_height(),
            background="black",
            cursor="cross",
        )
        self.canvas.grid(row=0, column=0, rowspan=self.row_span, sticky="nsew")

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def get_image_dir(self) -> None:
        image_dir = filedialog.askdirectory(
            initialdir=self.curr_dir,
            title="Choose image directory",
        )
        if not image_dir:
            return

        if self.canvas is None:
            self.setup_canvas()

        self.curr_dir = image_dir
        self.image_dir = Path(image_dir)
        self.colors = cycle(self.color_list)
        self.dirty = False

        paths = [
            p
            for p in sorted(self.image_dir.glob("*"))
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff")
        ]

        if paths:
            paths = sorted(p.name for p in paths)
            self.spinner_update(len(paths))
            canvas_height = self.image_frame.winfo_height()
            self.pages = [Page(self.image_dir / p, canvas_height) for p in paths]
            self.save_button.configure(state="normal")
            self.display_page()
        else:
            self.pages = []
            self.save_button.configure(state="disabled")
            self.spinner_clear()
            self.canvas.delete("all")

    def spinner_update(self, high: float) -> None:
        self.page_no.set(1)
        self.spinner.configure(state="normal")
        self.spinner.configure(from_=1)
        self.spinner.configure(to=high)

    def spinner_clear(self) -> None:
        self.page_no.set(0)
        self.spinner.configure(state="disabled")
        self.spinner.configure(from_=0)
        self.spinner.configure(to=0)

    def safe_quit(self) -> None:
        if self.dirty:
            yes = messagebox.askyesno(
                self.title(),
                "Are you sure you want to exit without saving?",
            )
            if not yes:
                return
        self.destroy()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
