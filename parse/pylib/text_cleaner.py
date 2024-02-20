MOJIBAKE = {
    "{": "(",
    "}": ")",
}
MOJIBAKE_WORDS = {
    # "find": "replace"
    r"Ivd": "lvd",
    r"Ivs": "lvs",
    r"1vd": "lvd",
    r"If-": "lf-",
    r"1f-": "lf-",
    r"If\.": "lf.",
    r"1f\.": "lf.",
    r"(?<=[a-z])U": "ll",
    r"-\s?l\b": "-1",
    r"\bl\s?-": "1-",
    r"-\s?l\s?l\b": "-11",
    r"\bl\s?l\s?-": "11-",
    r"\bl\s?1\b": "11",
    r"\bm\sm\b": "mm",
    r"1obe": "lobe",
    r"1eave": "leave",
    r"1eaf": "leaf",
    r"[Ili]\.(?=\d)": "1.",
    r"Unear": "Linear",
    r"tmnk": "trunk",
    r"(?<=[A-Za-z])/(?=[A-Za-z])": "l",
    r"//": "H",
    r"yar\.": "var.",
    r"var,": "var.",
    r"subsp,": "subsp.",
}
MOJIBAKE_REPLACE = {}


def make_sentences(nlp, text):
    doc = nlp(text)
    lines = [s.text + "\n" for s in doc.sents if s and s.text]
    return lines
