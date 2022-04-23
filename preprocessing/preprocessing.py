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
        p.process_header_footer()
        #p.delete_useless_contents()
        p.process_accents()
        # p.sort_y()

    print("APRES PREPROC\n")
    print("#####################", filename, "#####################")
    for p in pages:
        print(repr(p))

    processing.run(TextPreprocessingResult(filename, pages), final_stat)