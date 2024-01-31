import spacy
from traiter.pylib.pipes import tokenizer
from traiter.pylib.pipes.sentence import SENTENCES


def pipeline():
    nlp = spacy.load("en_core_web_sm", exclude=["ner", "lemmatizer", "tok2vec"])
    tokenizer.append_abbrevs(nlp, tokenizer.ABBREVS)
    tokenizer.append_abbrevs(nlp, tokenizer.PDF_ABBREVS)
    nlp.add_pipe(SENTENCES, before="parser")
    return nlp
