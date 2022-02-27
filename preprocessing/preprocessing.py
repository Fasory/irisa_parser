# -*-coding:utf-8 -*-

"""
This file is the main file of the pre-preocessing module.
"""

from .TextPreprocessingResult import TextPreprocessingResult
import processing


def run(extraction_result, target):
    filename = extraction_result.file_name
    pages = extraction_result.pages

    for p in pages:
        p.process_accents()

    organize_pages(pages)

    processing.run(TextPreprocessingResult(filename, pages), target)


# Gère les contents à cheval entre 2 pages
def organize_pages(pages):
    i = 0
    while i + 1 < len(pages):
        curr = pages[i]
        curr.organize_text()

        next = pages[i + 1]

        curr_last = curr.last_content()
        next_first = next.first_content()

        if curr_last.is_near(next_first):
            curr_last.merge_with(next_first)
            curr.change_last_content(curr_last)
            next.delete_first_content()

        i += 1
