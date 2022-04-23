# -*-coding:utf-8 -*-

"""
This source file contains all the classes allowing
to give a representation of a file after the
extraction of its data and metadata.
"""

from text_contents import TextAlignment, TextContentResult, TextPageResult


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

    def delete_out_of_bounds(self):
        for p in self._pages:
            p.delete_out_of_bounds()

    def compute_fonts(self):
        for p in self._pages:
            p.compute_fonts()
