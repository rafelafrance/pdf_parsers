# pdf_parsers
Utilities for parsing PDFs for information extraction

### Scripts for parsing PDFs

These scripts extract traits from PDFs containing plant treatments. The PDFs I'm parsing have rather complicated text flows. For example, a single page may jump from a 2-column format to a 1-column format several times in that page. The standard tools for converting PDFs to text were not handing these cases. So I wrote my own scripts to organize text from these documents. The work much better (for our use case) than the standard poppler libraries. _**Note: that these scripts are far from perfect, just better for our use cases.**_ Also note that, we still use the poppler utilities for parsing the PDFs, just not the text assembly part.

#### Main workflow for converting PDFs into text and then extracting traits:

1. [rename_pdfs.py](./flora/rename_pdfs.py) - This is an _**optional**_ step to make working with the PDFs a bit easier. All this utility does is replace problematic characters in a PDF file name (like space, parentheses, etc.) to underscores.
2. [pdf_to_images.py](./flora/pdf_to_images.py)
3. [slice.py](./flora/slice.py) - This script allows you to manually outline text on images from `pdf_to_images.py` with bounding boxes that contain treatment text. The boxes on a page must be in reading order. You need to mark which boxes are at the start of a treatment.
4. [stitch.py](./flora/stitch.py) This script takes the boxes from `slice.py` OCRs them and puts the text into a single output file.
5. [clean_text.py](./flora/clean_text.py) Now we take the text from the previous step and format it so that we can parse the text with spaCy rule-based parsers. This breaks the text into sentences, joins hyphenated words, fixes mojibake, removes control characters, space normalizes text, etc. Examine the output of this text to make sure things are still working as expected.
   1. The step for breaking the text into sentences is very slow.
6. [extract_traits.py](./flora/mimosa_extract_traits.py) Finally, we extract traits from the text using spaCy rule-based parsers.

#### Scripts that may help in PDF parsing projects:

1. [pdf_to_xhtml.py](./flora/pdf_to_xhtml.py) Convert a PDF into an XHTML document that contains the bounding box of every word in the document. This is used to build the pages.
   1. It's just a wrapper around the poppler utility `pdftotext -bbox -nodiag input.pdf output.xhtml`.
2. [xhtml_to_text.py](./flora/xhtml_to_text.py) Assembles the text.
   1. You need to edit the output to remove flow interrupting text such as page headers, footers, figure captions, etc.
   2. We do use margins for cropping pages that can help remove most headers & footers but pages may be skewed, so you should probably check for outliers.
3. [pdf_to_text.py](./flora/images_to_text.py) It tries to directly read text from a PDF. This may work on newer cleaner PDFs. If it works, then you can skip steps 1-4 above and pick up the main flow with `clean_text.py`.
4. [fix_page_nos.py](./flora/fix_page_nos.py) Use this if the images have odd page numbers that make pages out of order.

