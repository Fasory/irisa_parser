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

    listExtensions = []
    getExtensions(target, listExtensions)

    for extension in listExtensions :
        file_name = processingResult.original_file_name.replace(".pdf", extension)

        file_path = os.path.join(target.output, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'w', encoding='utf-8') as file:
            if (extension == ".txt"):
                restitutionText(file, processingResult)

            if (extension == ".xml"):
                restitutionXML(file, processingResult)


def restitutionText(file, processingResult):
        file.write("Fichier original : " + processingResult.original_file_name + "\n")

        file.write("Titre : " + processingResult.title)

        file.write("Auteurs : ")
        if len(processingResult.authors) > 0:
            file.write(processingResult.authors[0].name)
            if processingResult.authors[0].mail != "N/A":
                file.write(" (" + processingResult.authors[0].mail + ")")
            for author in processingResult.authors[1:]:
                file.write(", " + author.name)
                if author.mail != "N/A":
                    file.write(" (" + author.mail + ")")
        file.write("\n")

        file.write("Résumé : ")
        file.write(processingResult.abstract)
        file.write("\n")

        file.write("Références : " + processingResult.references)
        file.write("\n")


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
            file.write("\t\t<auteur>\n")
            file.write("\t\t\t<name>")
            file.write(author.name)
            file.write("</name>\n")
            file.write("\t\t\t<mail>")
            file.write(author.mail)
            file.write("</mail>\n")
            file.write("\t\t</auteur>\n")
    file.write("\t</auteurs>\n")

    file.write("\t<abstract>")
    file.write(processingResult.abstract)
    file.write("</abstract>\n")
    file.write("\t<biblio>")
    file.write(processingResult.references)
    file.write("</biblio>\n")
    file.write("</article>\n")

def addTab(file, nb) :
    return None

def getExtensions(target, listExtensions) : 
    if target._optionsList["text"] :
        listExtensions.append(".txt")
    if target._optionsList["xml"] :
        listExtensions.append(".xml")
    return listExtensions