#!/usr/bin/python
"""
Le controleur permet de vérifier les entrées du programme par :
- La vérification de la syntaxe de la commande ;
- La vérification de l'existence & des permissions du dossier d'entrée ;
- La vérification du format & des permissions des fichiers d'entrées.

-- Input : String (commande)
-- Output : Fichier
"""
import shutil
from os import listdir
from .FinalStat import FinalStat

import extraction
import os
import sys
import argparse
from alive_progress import alive_bar
from simple_term_menu import TerminalMenu
import inquirer

# import sys: Ce module donne accès à tous les arguments de ligne de commande


def run():
    controler()


def controler():
    # On vérifie qu'il n'y a qu'un seul et unique argument

    # Gestion des options
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--text", action='store_true', dest=".txt", help="select plain text result format")
    parser.add_argument('-x', "--xml", dest=".xml", action='store_true', help="select xml result format")
    parser.add_argument('-b', "--bypass", dest="#", action='store_true', help="bypass menu")
    parser.add_argument('input', help="the path of the input folder containing the pdf files")
    store = parser.parse_args()

    final_stat = FinalStat(vars(store)["input"], vars(store)["input"] + "/out")
    for key in vars(store):
        if key == "input":
            continue
        final_stat.addOption(key, vars(store)[key])

    pathDirectory = final_stat.input
    # On vérifie si le répertoire entré existe
    if not os.path.exists(pathDirectory):
        sys.exit("error -> <pathDirectory> does not exist")
    if not os.access(pathDirectory, os.F_OK | os.R_OK | os.W_OK):
        sys.exit("error -> you do not have write AND read permissions")

    PDFPath = []
    # On vérifie si le fichier a bien les droits de lecture ET d'écriture
    # Ajout de l'extension .pdf

    for file in listdir(pathDirectory):
        if os.access(os.path.join(pathDirectory, file), os.F_OK | os.R_OK | os.W_OK) and file[-4:] == ".pdf":
            PDFPath.append(os.path.join(pathDirectory, file))

    if final_stat.optionsList[".txt"] == False and final_stat.optionsList[".xml"] == False:
        options = [
            inquirer.Checkbox('options',
                              message="Choix des options",
                              choices=['XML', 'Texte'],
                              ),
        ]
        optionList = inquirer.prompt(options)

        for option in optionList["options"]:
            if option == 'XML' :
                final_stat.addOption(".xml", True)
                continue
            if option == 'Texte' :
                final_stat.addOption(".txt", True)
                continue

    convert = [
        inquirer.List('convert',
                          message="",
                          choices=['Choisir les documents à convertir', 'Quitter l\'application'],
                          ),
    ]
    selectionConvert = inquirer.prompt(convert)

    if selectionConvert.keys == "Quitter l\'application":
        exit()
    if selectionConvert["convert"] == "Choisir les documents à convertir":
        files_options = PDFPath
        files_options.append(" Tous les fichiers ")

        filePrompt = [
            inquirer.Checkbox('files',
                              message="Choix des fichiers",
                              choices=files_options,
                              ),
        ]
        selectFile = inquirer.prompt(filePrompt)
        print(selectFile.get("files"))
        if selectFile.get("files")[-1] == len(PDFPath) - 1:
            launch(final_stat, PDFPath)
        else :
            newPath = selectFile.get("files")
            launch(final_stat, newPath)

def launch(final_stat, PDFPath):
    # Remove du dossier et son contenu
    if os.path.exists(final_stat.output):
        shutil.rmtree(final_stat.output)

    # Conversion en txt
    with alive_bar(len(PDFPath)) as bar:
        for path in PDFPath:
            bar.text(path)
            extraction.run(path, final_stat)
            bar()
