import re
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

        # A MODIFIER
        self._words.append("summarizer")
        self._words.append("summarizers")

        self._title_no_re = re.compile(r"([0-9IiVvXxLl]+(\.[0-9IiVvXxLl])*(\.)?)|(1st)|(2nd)|(3rd)|([0-9]+th)$")

    def check_word(self, word):
        return word in self._words

    def check_no_proper_name(self, string):
        """Check if there is enough common words in a string"""
        words = string.split(" ")
        if len(words) == 0:
            return False

        valid_words = [w for w in words if (self._title_no_re.match(w) is None) and self.check_word(w)]
        #print("check npn: ", string, valid_words, words)
        return len(valid_words) / len(words) >= 0.5
