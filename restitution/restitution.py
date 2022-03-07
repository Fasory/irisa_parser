"""
This file is the main file of the restitution module
"""
import os
import sys


def run(processingResult, target):
    restitution(processingResult, target)


def restitution(processingResult, target):
    file_name = processingResult.original_file_name.replace(".pdf", ".txt")

    file_path = os.path.join(target._output, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, 'w', encoding='utf-8') as file:
        if not os.path.exists(target._output):
            os.mkdir(target._output)

        if (target._optionsList["text"]):
            restitutionText(file, processingResult)

        if (target._optionsList["xml"]):
            restitutionXML(file, processingResult)



def restitutionText(file, processingResult):
        file.write("Fichier original : " + processingResult.original_file_name + "\n")

        file.write("Titre : " + processingResult.title)

        file.write("Auteurs : ")
        if len(processingResult.authors) > 0:
            file.write(processingResult.authors[0])
        for author in processingResult.authors[1:]:
            file.write(", " + author)
        file.write("\n")

        file.write("Résumé : ")
        file.write(processingResult.abstract)


def restitutionXML(file, processingResult):
    addOpenBalise(file, "article")
    file.write()

def addOpenBalise(file, baliseName) :
    file.write("<" + baliseName + ">")

def addCloseBalise(file, baliseName):
    file.write("</" + baliseName + ">")
