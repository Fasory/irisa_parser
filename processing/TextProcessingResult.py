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

    def __init__(self, filename, title, authors, abstract, references):
        """
        Create TextProcessingResult with these 4 pieces of information:
            - PDF file name
            - the title
            - the authors
            - the abstract (if there is one)
            - the references (if there is one)
        """
        self._original_file_name = filename
        self._title = title
        self._authors = authors
        self._abstract = abstract
        self._references = references

    @property
    def original_file_name(self):
        """Get the filename"""
        return self._original_file_name

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

    @property
    def references(self):
        """Get the references"""
        return self._references


class Author:

    def __init__(self, name, mail=None):
        self._name = name
        self._mail = mail

    @property
    def name(self):
        """Get the name"""
        return self._name

    @property
    def mail(self):
        """Get the mail"""
        return self._mail

    @name.setter
    def name(self, value):
        self._mail = value
