import ftfy
import regex as re

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


def clean_text(
    text: str,
    trans: dict[int, str] | None = None,
    regexp: re.regex = None,
) -> str:
    text = text if text else ""

    text = text.translate(trans)  # Handle uncommon mojibake

    text = replace_patterns(regexp, text)  # Replace messed up words

    text = " ".join(text.split())  # Space normalize

    # Join hyphenated words when they are at the end of a line
    text = re.sub(r"([a-z])-\s+([a-z])", r"\1\2", text, flags=re.IGNORECASE)

    text = re.sub(r"(\d) (\d)", r"\1\2", text)  # Handle spaces between digits

    text = ftfy.fix_text(text)  # Handle common mojibake

    text = re.sub(r"\p{Cc}+", " ", text)  # Remove control characters

    return text


def build_replace_patterns() -> re.regex:
    replaces = []
    for i, (pattern, repl) in enumerate(MOJIBAKE_WORDS.items()):
        re_group_name = f"X{i:04d}"
        MOJIBAKE_REPLACE[re_group_name] = repl
        replaces.append(f"(?P<{re_group_name}>{pattern})")
    regexp: re.regex = re.compile("|".join(replaces))
    return regexp


def replace_patterns(regexp: re.regex, text: str) -> str:
    text = regexp.sub(lambda m: MOJIBAKE_REPLACE[m.lastgroup], text)
    return text
