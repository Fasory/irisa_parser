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

    def __init__(self, filename, title="N/A", authors="N/A", abstract="N/A", introduction="N/A", body="N/A",
                 discussion="N/A", conclusion="N/A", references="N/A"):
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
        self._introduction = introduction
        self._body = body
        self._discussion = discussion
        self._conclusion = conclusion
        self._references = references

    @property
    def original_file_name(self):
        """Get the filename"""
        return self._original_file_name

    @property
    def title(self):
        """Get the title"""
        return self._title

    @title.setter
    def title(self, val):
        self._title = val

    @property
    def authors(self):
        """Get the authors"""
        return self._authors

    @authors.setter
    def authors(self, val):
        self._authors = val

    @property
    def abstract(self):
        """Get the abstract"""
        return self._abstract

    @abstract.setter
    def abstract(self, val):
        self._abstract = val

    @property
    def introduction(self):
        """Get the introduction"""
        return self._introduction

    @introduction.setter
    def introduction(self, val):
        self._introduction = val

    @property
    def body(self):
        """Get the body"""
        return self._body

    @body.setter
    def body(self, val):
        self._body = val

    @property
    def discussion(self):
        """Get the discussion"""
        return self._discussion

    @discussion.setter
    def discussion(self, val):
        self._discussion = val

    @property
    def conclusion(self):
        """Get the conclusion"""
        return self._conclusion

    @conclusion.setter
    def conclusion(self, val):
        self._conclusion = val

    @property
    def references(self):
        """Get the references"""
        return self._references

    @references.setter
    def references(self, val):
        self._references = val


class Author:

    def __init__(self, name, mail="N/A", affiliation="N/A"):
        self._name = name
        self._mail = mail
        self._affiliation = affiliation

    @property
    def name(self):
        """Get the name"""
        return self._name

    @property
    def mail(self):
        """Get the mail"""
        return self._mail

    @property
    def affiliation(self):
        """Get the affiliation"""
        return self._affiliation

    @name.setter
    def name(self, value):
        self._mail = value
