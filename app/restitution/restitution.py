"""
This file is the main file of the restitution module
"""
import os
from app.controller.controller import OUTPUT_DIR
from processing import TextProcessingResult

def run(processingResult : TextProcessingResult):
    restitution(processingResult)

def restitution(processingResult : TextProcessingResult) :
    file_name = processingResult.original_file_name().replace(".pdf",".txt")

    file_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.exists(file_path) :
        os.remove(file_path)
    if os.path.exists(OUTPUT_DIR) :
        os.remove(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)

    file = open(file_path, "rwx")

    file.write(processingResult.title)

    for author in processingResult.authors() :
        file.write(author)
    
    file.write(processingResult.abstract())