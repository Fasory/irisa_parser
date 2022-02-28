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
        p.merge_all()
        p.process_accents()

    print("###########################################################")
    print("FIN PREPROC")
    for p in pages:
        for c in p.contents:
            print("CONTENT\n", c)

    processing.run(TextPreprocessingResult(filename, pages), target)
