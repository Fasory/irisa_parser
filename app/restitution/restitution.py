"""
To do
"""
import os
from app.controller.controller import OUTPUT_DIR
from processing import TextProcessingResult

def run(processingResult : TextProcessingResult):
    
    file_name = processingResult.original_file_name().replace(".pdf",".txt")

    file_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.exists(file_path) :
        os.remove(file_path)
    if os.path.exists(OUTPUT_DIR) :
        os.remove(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)

    file = open(file_path, "rwx")

    file.write(processingResult.title)
    file.write(processingResult.authors())
    file.write(processingResult.abstract())