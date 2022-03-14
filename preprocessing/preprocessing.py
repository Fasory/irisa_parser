# -*-coding:utf-8 -*-

"""
This file is the main file of the pre-preocessing module.
"""

from .TextPreprocessingResult import TextPreprocessingResult
import processing


def run(extraction_result, final_stat):
    filename = extraction_result.file_name
    pages = extraction_result.pages

    for p in pages:
        p.sort_y()
        p.process_accents()

    print("APRES PREPROC\n")
    print("#####################", filename, "#####################")
    for p in pages:
        print("-------AUTRE PAGE-------------")
        for c in p.contents:
            print("CONTENT\n", c)

    processing.run(TextPreprocessingResult(filename, pages), final_stat)
