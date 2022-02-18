# -*-coding:utf-8 -*-

"""
This source file contains all the classes allowing
to give a representation of a file after the
extraction of its data and metadata.
"""

from pdfminer.layout import LTTextContainer
from enum import Enum, unique


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
            raise TypeError("must be TextPageResult, not " + type(other).__name__)
        self._pages.append(other)
        return self


class TextPageResult:
    """
    This class represents the extraction of a page from
    a file. It gathers the number of the extracted page
    and a list of its content.
    """
    def __init__(self, number):
        """ Constructor """
        if not isinstance(number, int):
            raise TypeError("must be int, not " + type(number).__name__)
        self._number = number
        self._contents = []

    @property
    def number(self):
        """ Get page number """
        return self._number

    @property
    def contents(self):
        """ Get page content """
        return self._contents

    def __add__(self, other):
        """ Adds a new TextContentResult to the list of contents """
        if not isinstance(other, TextContentResult):
            raise TypeError("must be TextContentResult, not " + type(other).__name__)
        self._contents.append(other)
        return self


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
            raise TypeError("must be LTTextContainer, not " + type(elt).__name__)
        self._string = elt.get_text()
        self._position = elt.bbox
        self._font_sizes = {}
        self._fonts = {}
        self._alignments = {TextAlignment.HORIZONTAL : 0, TextAlignment.VERTICAL : 0}

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
    def alignments(self):
        """ Get dictionnary of alignments """
        return self._alignments


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1