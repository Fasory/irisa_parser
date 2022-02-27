# -*-coding:utf-8 -*-

"""
This source file contains all the classes allowing
to give a representation of a file after the
extraction of its data and metadata.
"""

import copy
from enum import Enum, unique
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTTextLineVertical, LTChar, LTTextLine


class TextExtractionResult:
    """
    This class represents the final result of the extraction
    of data and metadata from a file. It gathers the name of
    the original file and a list of extracted pages.
    """

    def __init__(self, path):
        """ Constructor """
        if not isinstance(path, str):
            raise TypeError("must be str, not " + type(path).__name__)
        self._file_name = path
        self._pages = []

    @property
    def file_name(self):
        """ Get file name """
        return self._file_name

    @property
    def pages(self):
        """ Get pages """
        return self._pages

    def __add__(self, other):
        """ Adds a new TextPageResult to the list of extracted pages """
        if not isinstance(other, TextPageResult):
            raise TypeError("must be TextPageResult, not " +
                            type(other).__name__)
        self._pages.append(other)
        return self


class TextPageResult:
    """
    This class represents the extraction of a page from
    a file. It gathers the number of the extracted page
    and a list of its content.
    """

    def __init__(self, number, width, height):
        """ Constructor """
        if not isinstance(number, int):
            raise TypeError("must be int, not " + type(number).__name__)
        self._number = number
        self._contents = []
        self._width = width
        self._height = height

    @property
    def number(self):
        """ Get page number """
        return self._number

    @property
    def contents(self):
        """ Get page content """
        return self._contents

    @property
    def width(self):
        """ Get width """
        return self._width

    @property
    def height(self):
        """ Get height """
        return self._height

    def __add__(self, other):
        """ Adds a new TextContentResult to the list of contents """
        if not isinstance(other, TextContentResult):
            raise TypeError(
                "must be TextContentResult, not " + type(other).__name__)
        self._contents.append(other)
        return self

    def first_content(self):
        return self._contents[0]

    def delete_first_content(self):
        self._contents.pop(0)

    def last_content(self):
        return self._contents[-1]

    def change_last_content(self, content):
        self._contents[-1] = content

    def contents_higher(self):
        proper = []
        limit = self._height / 2
        for content in self._contents:
            if min(content.position[1], content.position[3]) <= limit:
                proper.append(content)
        return proper

    def contents_lower(self):
        proper = []
        limit = self._height / 2
        for content in self._contents:
            if min(content.position[1], content.position[3]) > limit:
                proper.append(content)
        return proper

    def process_accents(self):
        for c in self._contents:
            c.process_accents()

    def organize_text(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            # Fusionne toute la chaîne (si +2 self._contents à fusionner)
            j = i
            merged = self._contents[j]
            while j + 1 < len(self._contents) and self._contents[j].is_near(self._contents[j + 1]):
                next = self._contents[j + 1]
                merged.merge_with(next)

                j += 1

            new_contents.append(merged)

            i = j
            i += 1

        self._contents = new_contents


class TextContentResult:
    """
    This class represents a targeted data block of a file.
    It is characterized by a character string, a list of
    used fonts, a list of used size and the position of
    the block on the page from which it comes.
    """

    def __init__(self, elt):
        """ Constructor """
        if not isinstance(elt, LTTextContainer):
            raise TypeError("must be LTTextContainer, not " +
                            type(elt).__name__)
        self._container = elt
        self._string = elt.get_text()
        self._position = elt.bbox
        self._font_sizes = {}
        self._fonts = {}
        self._alignment = None
        for line in elt:
            # define alignment
            if isinstance(line, LTTextLineHorizontal):
                if self._alignment is None:
                    self._alignment = TextAlignment.HORIZONTAL
                elif self._alignment is TextAlignment.VERTICAL:
                    self._alignment = TextAlignment.UNDEFINED
            elif isinstance(line, LTTextLineVertical):
                if self._alignment is None:
                    self._alignment = TextAlignment.VERTICAL
                elif self._alignment is TextAlignment.HORIZONTAL:
                    self._alignment = TextAlignment.UNDEFINED
            if isinstance(line, LTChar):
                if line.size not in self._font_sizes.keys():
                    self._font_sizes[line.size] = 0
                self._font_sizes[line.size] += 1
                if line.fontname not in self._fonts.keys():
                    self._fonts[line.fontname] = 0
                self._fonts[line.fontname] += 1
            elif isinstance(line, LTTextLine):
                for char in line:
                    if isinstance(char, LTChar):
                        if char.size not in self._font_sizes.keys():
                            self._font_sizes[char.size] = 0
                        self._font_sizes[char.size] += 1
                        if char.fontname not in self._fonts.keys():
                            self._fonts[char.fontname] = 0
                        self._fonts[char.fontname] += 1

    def hdistance(self, other_content):
        return self._container.hdistance(other_content.container)

    def vdistance(self, other_content):
        return self._container.vdistance(other_content.container)

    @property
    def container(self):
        return self._container

    @property
    def string(self):
        """ Get raw string of content """
        return self._string

    @property
    def position(self):
        """ Get position of content """
        return self._position

    @property
    def font_sizes(self):
        """ Get dictionnary of font sizes """
        return self._font_sizes

    @property
    def fonts(self):
        """ Get dictionnary of fonts """
        return self._fonts

    @property
    def alignment(self):
        """ Get alignment """
        return self._alignment

    def major_font(self):
        return max(self._fonts, key=self._fonts.get)

    def major_font_size(self):
        return max(self._font_sizes, key=self._font_sizes.get)

    def process_accents(self):
        self._string.replace("'A", "Á")
        self._string.replace("¨A", "Ä")
        self._string.replace("`A", "À")
        self._string.replace("^A", "Â")
        self._string.replace("'a", "á")
        self._string.replace("¨a", "ä")
        self._string.replace("`a", "à")
        self._string.replace("^a", "â")
        self._string.replace("'E", "É")
        self._string.replace("¨E", "Ë")
        self._string.replace("`E", "È")
        self._string.replace("^E", "Ê")
        self._string.replace("'e", "é")
        self._string.replace("¨e", "ë")
        self._string.replace("`e", "è")
        self._string.replace("^e", "ê")

    def is_near(self, other_content):
        # Mot coupé entre 2 contents => true
        self_words = self._string.split(" ")
        other_words = other_content.string.split(" ")

        last_word = self_words[-1]
        first_word_other = other_words[0]  # premier mot de other_content
        if last_word.endswith("-"):
            recreated_word = last_word[:-1] + first_word_other
            if TextContentResult._check_word(recreated_word):
                return True

        # Police ou taille différente => false
        if self.major_font().lower() != other_content.major_font().lower() or self.major_font_size() != other_content.major_font_size():
            return False

        # Distance trop grande => false
        # if

        return True

    @staticmethod
    def _check_word(word):
        return True  # condition à faire avec spacy

    def merge_with(self, other_content):
        # Splitted word
        self_words = self._string.split(" ")
        other_words = other_content.string.split(" ")

        last_word = self_words[-1]
        first_word_other = other_words[0]  # premier mot de other_content

        insert_char = ""
        if last_word.endswith("-"):
            recreated_word = last_word[:-1] + first_word_other
            if TextContentResult._check_word(recreated_word):
                # reconstitue dernier mot de self
                self_words[-1] = recreated_word
                # supprime premier mot de other_content
                other_words = other_words[1:]

                insert_char = " "  # si dernier mot reconstitué, on insère un espace entre les 2 parties

        self._string = " ".join(self_words) + \
                       insert_char + " ".join(other_words)

        self._position = (self._position[0], self._position[1], other_content.position[2], self._position[3])
        self._position = (self._position[0], self._position[1], self._position[2], other_content.position[3])


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    UNDEFINED = 2
