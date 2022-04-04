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

    # Remove du dossier et son contenu
    if os.path.exists(final_stat.output):
        shutil.rmtree(final_stat.output)

    # Conversion en txt
    with alive_bar(len(PDFPath)) as bar :
        for path in PDFPath:
            bar.text(path)
            # DEBUG ############
            # if not "METICS" in path:
            #    continue
            ####################
            # print("Convert file " + path + "...")
            extraction.run(path, final_stat)
            bar()
            
