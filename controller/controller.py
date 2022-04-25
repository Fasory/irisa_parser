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


# import sys: Ce module donne accès à tous les arguments de ligne de commande


def run():
    controler()


def controler():
    # On vérifie qu'il n'y a qu'un seul et unique argument

    # Gestion des options
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--text", action='store_true', dest=".txt", help="select plain text result format")
    parser.add_argument('-x', "--xml", dest=".xml", action='store_true', help="select xml result format")
    parser.add_argument('input', help="the path of the input folder containing the pdf files")
    store = parser.parse_args()

    final_stat = FinalStat(vars(store)["input"], vars(store)["input"] + "/out")
    for key in vars(store):
        if (key == "input"):
            continue
        final_stat.addOption(key, vars(store)[key])

    pathDirectory = final_stat.input
    # On vérifie si le répertoire entré existe
    if os.path.exists(pathDirectory) != True:
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
        options_opt_menu = ["XML", "Texte"]
        options_menu = TerminalMenu(options_opt_menu, multi_select=True, show_multi_select_hint=True, title="Choisir les options")
        options_menu_index = options_menu.show()
        for option in options_menu_index :
            if option == 0 :
                final_stat.addOption(".xml", True)
                continue
            if option == 1 :
                final_stat.addOption(".txt", True)
                continue

    options = ["Choisir les fichiers à garder", "Fermer le programme"]
    main_menu = TerminalMenu(options)
    menu_menu_index = main_menu.show()

    if menu_menu_index == 1:
        exit()
    if menu_menu_index == 0:
        files_options = PDFPath
        files_options.append(" Tous les fichiers ")
        select_menu = TerminalMenu(files_options, multi_select=True, show_multi_select_hint=True)
        select_menu_index = select_menu.show()

        if select_menu_index[-1] == len(PDFPath) - 1:
            launch(final_stat, PDFPath)
        else :
            newPath = []
            for index in select_menu_index :
                newPath.append(PDFPath[index])
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
