# -*-coding:utf-8 -*-

"""
This file contains all the classes which allow
to represent the text processing result
"""


class TextProcessingResult:
    """
    Result of the processing step. It contains all the
    data needed to write the output text file
    """

    def __init__(self, filename, title, authors, abstract):
        """
        Create TextProcessingResult with these 4 pieces of information:
            - PDF file name
            - the title
            - the authors
            - the abstract (if there is one)
        """
        self._original_filename == filename
        self._title = title
        self._authors = authors
        self._abstract = abstract

    @property
    def original_filename(self):
        """Get the filename"""
        return self._original_filename

    @property
    def title(self):
        """Get the title"""
        return self._title

    @property
    def authors(self):
        """Get the authors"""
        return self._authors

    @property
    def abstract(self):
        """Get the abstract"""
        return self._abstract
