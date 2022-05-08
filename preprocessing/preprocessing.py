# -*-coding:utf-8 -*-

"""
This file is the main file of the pre-processing module.
"""

from .TextPreprocessingResult import TextPreprocessingResult
import processing

DEBUG = False

def run(extraction_result, final_stat):
    filename = extraction_result.file_name
    pages = extraction_result.pages

    preprocessed = TextPreprocessingResult(filename, pages)
    #preprocessed.print_result()
    preprocessed.print_pages()
    if not DEBUG:
        processing.run(preprocessed, final_stat)
        
