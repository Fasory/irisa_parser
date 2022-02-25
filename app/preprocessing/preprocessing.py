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
    while i < len(contents):
        # Fusionne toute la chaîne (si +2 contents à fusionner)
        j = i
        merged = contents[j]
        while j + 1 < len(contents) and contents[j].is_near(contents[j + 1]):
            next = contents[j + 1]
            merged = merged.merge_with(next)

            j += 1

        new_contents.append(merged)

        i = j
        i += 1

    return new_contents
