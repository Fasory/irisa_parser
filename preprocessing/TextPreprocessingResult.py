# -*-coding:utf-8 -*-

"""
This source file contains all the classes allowing
to give a representation of a file after the
pre-processing.
"""


class TextPreprocessingResult:
    """
    Represent the pre-processing result. It stores the content,
    as TextExtractionResult.
    """

    def __init__(self, filename, pages):
        """Initializes the pre-processing result"""
        self._filename = filename
        self._pages = pages
        self._major_font = None
        self._major_font_size = None

    @property
    def filename(self):
        """Get PDF file name"""
        return self._filename

    @property
    def pages(self):
        """Get the pages"""
        return self._pages

    @property
    def major_font(self):
        """Get the major font name"""
        return self._major_font

    @property
    def major_font_size(self):
        """Get the major font size"""
        return self._major_font_size
