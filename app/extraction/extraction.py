# -*-coding:utf-8 -*-

"""
This file is the main file of the extraction module.
"""

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer

import app.processing as processing
from TextExtractionResult import TextExtractionResult, TextPageResult, TextContentResult


def run(path):
    """ Main function of module """
    processing.run(extraction(path))


def extraction(path):
    result = TextExtractionResult(path)
    current_number = 0
    for page in extract_pages(path, laparams = LAParams(char_margin = 20, all_texts = True)):
        current_number += 1
        current_page = TextPageResult(current_number)
        for content in page:
            if isinstance(content, LTTextContainer):
                current_page += TextContentResult(content)
        result += current_page
    return result
