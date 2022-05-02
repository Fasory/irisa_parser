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
import inquirer


def run():
    controler()


def controler():
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

        optionsList = {"options": []}
        while len(optionsList.get("options")) == 0:
            options = [
                inquirer.Checkbox('options',
                                  message="Choix des options (ESPACE pour sélectionner, ENTER pour valider)",
                                  choices=[('XML', 0), ('Texte', 1)],
                                  ),
            ]
            optionsList = inquirer.prompt(options)


            if len(optionsList.get("options")) == 0:
                print("\033[93m /!\ Selection d'options vides, appuyez sur ENTER pour selectionner une ou plusieurs options")
                continue


            for option in optionsList.get("options"):
                if option == 0:
                    final_stat.addOption(".xml", True)
                if option == 1:
                    final_stat.addOption(".txt", True)



    convert = [
        inquirer.List('convert',
                      message="",
                      choices=[('Choisir les documents à convertir', 0), ('Quitter l\'application', 1)],
                      ),
    ]
    selectionConvert = inquirer.prompt(convert)

    if selectionConvert.get("convert") == 1:
        exit()
    if selectionConvert.get("convert") == 0:
        selectFile = {"files": []}
        while len(selectFile.get('files')) == 0:
            filePrompt = [
                inquirer.Checkbox('files',
                                  message="Choix des fichiers (ESPACE pour sélectionner, ENTER pour valider)",
                                  choices=PDFPath + ["Tous les fichiers"],
                                  ),
            ]
            selectFile = inquirer.prompt(filePrompt)
            if len(selectFile.get("files")) == 0:
                print("\033[93m /!\ Selection de fichiers vide, appuyez sur ENTER pour selectionner un ou des fichiers")
                continue
            if selectFile.get("files")[-1] == "Tous les fichiers":
                launch(final_stat, PDFPath)
            else:
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
