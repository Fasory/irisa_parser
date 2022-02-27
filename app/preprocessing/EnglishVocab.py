import spacy


class EnglishVocab:
    __instance = None

    @staticmethod
    def instance():
        if EnglishVocab.__instance is None:
            EnglishVocab.__instance = EnglishVocab()

        return EnglishVocab.__instance

    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm")
        self._words = list(self._nlp.vocab.strings)

    def check_word(self, word):
        return word in self._words
