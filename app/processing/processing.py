"""
Processing step
"""

from TextProcessingResult import TextProcessingResult
from app import restitution


def run(result):
    restitution.run(TextProcessingResult(result.filename,
                                         find_title(result.contents),
                                         find_authors(result.contents),
                                         find_abstract(result.contents)))


def find_title(contents):
    pass


def find_authors(contents):
    pass


def find_abstract(content):
    pass
