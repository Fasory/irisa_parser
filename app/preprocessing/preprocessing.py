# -*-coding:utf-8 -*-

"""
This file is the main file of the pre-preocessing module.
"""

from TextPreprocessingResult import TextPreprocessingResult
import processing


def run(extraction_result):
    filename = extraction_result.file_name
    pages = extraction_result.pages

    contents = []
    for p in pages:
        for c in p.contents:
            contents.append(c)

    contents = organize_text(contents)

    processing.run(TextPreprocessingResult(filename, contents))


def organize_text(contents):
    new_contents = []

    i = 0
    while i < len(contents) - 1:
        c1 = contents[i]
        c2 = contents[i + 1]

        merged = c1
        while c1.is_near(c2) and i < len(contents) - 1:
            merged = merged.merge_with(c2)

            i += 1
            c1 = contents[i]
            c2 = contents[i + 1]

        i += 1

    return new_contents
