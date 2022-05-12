# -*-coding:utf-8 -*-

"""
The purpose of this module is to parse the pre-processed text, and to extract
different sections to restitute (the title, the authors, and the whole text)

This module follows the preprocessing module and
precedes the restitution module.
"""

# info
__version__ = "1.0"
__author__ = "Clément BOUQUET"

from .processing import run
from .TextProcessingResult import TextProcessingResult