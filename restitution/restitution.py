"""
This file is the main file of the restitution module
"""
import os
import sys
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom

def run(processingResult, final_stat):
    restitution(processingResult, final_stat)


def restitution(processingResult, target):
    if not os.path.exists(target.output):
        os.mkdir(target.output)

    listExtensions = target.optionsList

    for extension in listExtensions:
        if(listExtensions[extension] == False) :
            continue

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
    root = Element('article')
    preamble = SubElement(root, "preambule")
    preamble.text = "Fichier original : " + processingResult.original_file_name

    title = SubElement(root, "titre")
    title.text = "Titre : " + processingResult.title

    if len(processingResult.authors) > 0:
        authors = SubElement(root, "auteurs")
        for author in processingResult.authors:
            auth = SubElement(authors, "auteur")
            name = SubElement(auth, "nom")
            name.text = author.name
            mail = SubElement(auth, "mail")
            mail.text = author.mail

    abstract = SubElement(root, "abstract")
    abstract.text = processingResult.abstract

    references = SubElement(root, "references")
    references.text = processingResult.references


    file.write(minidom.parseString(tostring(root)).toprettyxml(indent="  "))