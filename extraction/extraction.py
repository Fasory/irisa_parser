# -*-coding:utf-8 -*-

"""
This file is the main file of the extraction module.
"""
import os.path

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer, LTFigure

import preprocessing
from .TextExtractionResult import TextExtractionResult, TextPageResult, TextContentResult


def run(path, final_stat):
    """ Main function of module """

    extracted = extraction(path)
    extracted.compute_fonts()
    #print("APRES EXTRACTION\n")
    #print("#####################", path, "#####################")
    #for p in extracted.pages:
    #    print(p)

    preprocessing.run(extracted, final_stat)


def extraction(path):
    result = TextExtractionResult(os.path.basename(path))
    current_number = 0
    for page in extract_pages(path, laparams=LAParams(char_margin=20, all_texts=True)):
        current_number += 1
        current_page = TextPageResult(current_number, page.width, page.height)
        for content in page:
            if isinstance(content, LTFigure):
                current_page = figure_recurring(current_page, content)
            elif isinstance(content, LTTextContainer):
                current_page += TextContentResult(content)
        result += current_page
    return result


def figure_recurring(current_page, figure):
    for content in figure:
        if isinstance(content, LTFigure):
            current_page = figure_recurring(current_page, content)
        elif isinstance(content, LTTextContainer):
            current_page += TextContentResult(content)
    return current_page
