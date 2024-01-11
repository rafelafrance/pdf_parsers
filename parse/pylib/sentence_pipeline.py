from spacy.lang.en import English

from traiter.pylib.pipes import tokenizer
from traiter.pylib.pipes.sentence import SENTENCES


def pipeline():
    nlp = English()
    tokenizer.setup_tokenizer(nlp)
    nlp.add_pipe(SENTENCES, config={"abbrev": tokenizer.ABBREVS})
    return nlp
