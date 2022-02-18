# -*-coding:utf-8 -*-

"""
This file is the main file of the extraction module.
"""

import app.processing as processing
import TextExtractionResult

def run(path):
    """ Main function of module """
    processing.run(TextExtractionResult(path))