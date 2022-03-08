"""
This file is the main file of the restitution module
"""
import os
import sys


def run(processingResult, final_stat):
    restitution(processingResult, final_stat)


def restitution(processingResult, target):
    if not os.path.exists(target.output):
        os.mkdir(target.output)

    file_name = processingResult.original_file_name.replace(".pdf", ".txt")

    file_path = os.path.join(target.output, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, 'w', encoding='utf-8') as file:

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
    file.write("<article>\n")

    file.write("\t<preamble>")
    file.write("Fichier original : " + processingResult.original_file_name)
    file.write("</preamble>\n")

    file.write("\t<titre> ")
    file.write("Titre : " + processingResult.title)
    file.write("</titre> \n")

    if len(processingResult.authors) > 0:
        file.write("\t<auteurs>\n")
        for author in processingResult.authors:
            file.write("\t\t<auteur>")
            file.write("\t\t\t<name>")
            file.write(author.name)
            file.write("</name>\n")
            file.write("\t\t\t<mail>")
            file.write(author.mail)
            file.write("</mail>\n")
            file.write("\t\t</auteur>")
        file.write("</auteurs>\n")

    file.write("\t<abstract>")
    file.write(processingResult.abstract)
    file.write("<abstract>\n")
    file.write("\t<biblio>\n")

    file.write("\t</biblio>\n")
    file.write("</article>\n")

def addTab(file, nb) :
    return None