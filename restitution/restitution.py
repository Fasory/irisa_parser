"""
This file is the main file of the restitution module
"""
import os
import sys


def run(processingResult, OUTPUT_DIR):
    restitution(processingResult, OUTPUT_DIR)


def restitution(processingResult, OUTPUT_DIR):
    file_name = processingResult.original_file_name.replace(".pdf", ".txt")

    file_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("Titre : ")
        file.write(processingResult.title)

        file.write("Auteurs : ")
        if len(processingResult.authors) > 0:
            file.write(processingResult.authors[0])
        for author in processingResult.authors[1:]:
            file.write(", " + author)
        file.write("\n")

        file.write("Résumé : ")
        file.write(processingResult.abstract)
