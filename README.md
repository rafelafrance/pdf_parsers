# pdf_parsers

Utilities for parsing PDFs for information extraction.

1. [Description](#Description)
2. [Install](#Install)
3. [Utilities](#Utilities)
4. [Scenario: PDF has text](#PDF-has-text)
5. [Scenario: OCR PDF](#OCR-PDF)

## Description

These scripts extract traits from PDFs containing treatments. The PDFs I'm parsing have rather complicated text flows. For example, a single page may jump from a 2-column format to a 1-column format several times in that page. It may also have header, footers, figures, captions too. Other PDFs are just wrappers around images. The standard tools for converting PDFs to text were not handing these particular cases. So I wrote my own scripts to organize text from these documents. I had mixed results.

_**Note: that these scripts are far from perfect, just sometimes useful for our use cases.**_

**Also note that you will almost certainly need to edit the output text files to make then usable for information extraction.**

## Install

Install the poppler utilities. On Ubuntu Linux this looks like: `sudo apt install poppler-utils`.

If you need to OCR PDFs you need to install tesseract (Ubuntu) like: `sudo apt install tesseract-ocr`.

You can install script requirements into your python virtual environment like so:

```bash
git clone https://github.com/rafelafrance/pdf_parsers.git
cd /path/to/pdf_parsers
make install
```

Every time you want to run any scripts in a new terminal session you will need to activate the virtual environment, once, before running them.

```bash
cd /path/to/pdf_parsers
source .venv/bin/activate
```

## Utilities

### Rename PDFs

This is strictly a personal preference, but I like to keep the PDF names free of spaces and other odd characters. Have a backup before running this utility.

```bash
rename-pdfs --pdf-dir /path/to/pdfs
```

### Ad hoc scripts

TODO formalize these scripts.

```bash
python parse/adhocery.py ...
```

## PDF has text

The first thing you want to try is to extract text from the PDF directly. If the text is actually there then you want to use this text because everything else is typically much worse.

Things to look out for:
- You actually got all the text. I have encountered many PDFs that only have extractable text in a fraction of the pages.
- The characters are the same as they appear on the page. PDFs can use their own character maps, so you may encounter something like a "%" being mapped to a "♀" symbol. This probably won't stop you from using the extracted text, but it is confusing, and may need editing.
- Are header, footers, figure captions, tables, TOC, footnotes, etc. in the extracted text? If so, then remove them.
- Are the treatments clearly delineated? If they are then you can programmatically separate them into separate files. If they are not, then you will want to put markers into the text so that you can split them programmatically.
- In short, PDFs are evil and be on your guard when extracting text from them.

### Scenario: The text is in order

Then you can use the wrapper around the poppler tools to extract text.

Example:

```bash
pdftotext -layout -x 0 -y 50 -W 1275 -H 1600 /path/to/pdfs/treatments.pdf /path/to/text/treatments.txt
```

You will need to change the arguments for your situation. `pdftotext -h`.

### There are some ordering issues with the text

Sometimes the text is all there, but it is out of order. These scripts extract the text with each phrase's location on the page. And try to assemble them into the proper order. _**Extracting text using these scripts is iffy.**_

#### Convert to XHTML

Convert a PDF into an XHTML document that contains the bounding box of every word in the document. This script is just a wrapper around the poppler utility `pdftotext -bbox -nodiag input.pdf output.xhtml`.

Example:

```bash
pdf-to-xhtml --in-pdf /path/to/treatments.pdf --out-xhtml /path/to/treatments.xhtml
```

#### XHTML to text

Try to assemble the text into the proper order. Getting the arguments right is a trick, but it has worked for me in some cases.

```bash
xhtml-to-text --in-xhtml /path/to/treatments.xhtml --out-text /path/to/treatments.txt
```

Other arguments:
- `--gap-radius`: Consider a gap to be in the center if it is within this distance of the true center of the page.
- `--gap-min`: Break a line into 2 columns if the gap between words is near the center and the gap is at least this big. Set this to zero if there are never 2 columns of text.
- `--min-y`: Remove words that are above this distance (in pixels) from the top of the page.
- `--max-y`: Remove words that are below this distance (in pixels) from the bottom of the page.

## OCR PDF

This sequence of scripts coverts a PDF to images and the OCRs the images to get text.

### Convert PDFs to images

First we need to convert the PDF into images so that we can run an OCR program on it. This script output one image file per page.

Example:

```bash
pdf-to-images --in-pdf /path/to/treatments.pdf --image-dir /path/to/treatment/images
```

### Fix image page numbers

Sometimes the `pdf-to-images` output has names that do not sort in order, which will mess up the `slice-gui` script (below). This utility may fix this. I rarely need this utility, but when you need it, you will be glad you have it.

Example:

```bash
fix-page-nos --image-dir /path/to/treatment/images --glob '*.jpg'
```

### Slice images into text areas

This script allows you to manually outline text on images from `pdf-to-images` with bounding boxes that contain treatment text. The boxes on a page must be in reading order. You need to mark which boxes are at the start of a treatment.

The output is a JSON file that holds the images paths and notes about the boxes drawn on them.

Example:

```bash
slice-gui
```

[<img src="assets/slice_example.png" width="800" />](assets/slice_example.png)

In this example the areas start at the top left and end at the bottom right, going down the columns. In order:

1. The top left box (red) holds the final text from a previous treatment.
2. The bottom left box (blue) holds the start of the next treatment. The treatment start is indicated by a dashed box.
3. The top right box (green) holds the second portion of the treatment started in #2.
4. The bottom right box (black) holds the start of another treatment. Another dashed box.

- Notice that the header and key in the middle of the right column are skipped.
- You are able to mark boxes as "clear area" which I use to remove diagrams that are embedded in the text and would be cumbersome to draw boxes around.

### OCR text from slices

This script takes the boxes from `slice-gui` OCRs them and puts the text into separate files, one per treatment.

Example:

```bash
stitch --in-json /path/to/slice.json --treatment-template /template/for/treatment.txt
```

### Clean OCR text

Now we take the text from the previous step and format it so that we can parse the text with spaCy rule-based parsers. This joins hyphenated words, fixes mojibake, removes control characters, space normalizes text, etc. Examine the output of this text to make sure things worked as expected.

Example:

```bash
clean-text --dirty-dir /path/to/treatments --clean-dir /path/to/clean/treatments
```
