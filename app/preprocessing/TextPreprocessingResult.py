# -*-coding:utf-8 -*-

"""
This source file contains all the classes allowing
to give a representation of a file after the
pre-processing.
"""


class TextPreprocessingResult:
    """
    Represent the pre-processing result. It stores the content,
    as TextExtractionResult, but not splitted in pages.
    """

    def __init__(self, filename, contents):
        """Initializes the pre-processing result"""
        self._filename = filename
        self._contents = contents

    @property
    def filename(self):
        """Get PDF file name"""
        return self._filename

    @property
    def contents(self):
        """Get the whole content"""
        return self._contents
