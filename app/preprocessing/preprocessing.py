# -*-coding:utf-8 -*-

"""
This file is the main file of the pre-preocessing module.
"""

from TextPreprocessingResult import TextPreprocessingResult


def run(extraction_result):
    filename = extraction_result.file_name
    pages = extraction_result.pages

    contents = []
    for p in pages:
        for c in p.contents:
            contents.append(c)

    return TextPreprocessingResult(filename, contents)


def organize_text(contents):
    new_contents = []

    i = 0
    while i < len(contents):
        c1 = contents[i]
        c2 = contents[i + 1]
