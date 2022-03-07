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


# import sys: Ce module donne accès à tous les arguments de ligne de commande


def run():
    controler()


def controler():
    # On vérifie qu'il n'y a qu'un seul et unique argument

    # Gestion des options
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--text", action='store_true', help="select plain text result format")
    parser.add_argument('-x', "--xml", action='store_true', help="select xml result format")
    parser.add_argument('input', help="the path of the input folder containing the pdf files")
    store = parser.parse_args()

    pathDirectory = store.__dict__.get("input")

    # On vérifie si le répertoire entré existe
    if os.path.exists(pathDirectory) != True:
        sys.exit("error -> <pathDirectory> does not exist")
    if not os.access(pathDirectory, os.F_OK | os.R_OK | os.W_OK):
        sys.exit("error -> you do not have write AND read permissions")

    final_stat = FinalStat(pathDirectory, os.path.join(pathDirectory, "out"))
    final_stat.addOption("xml", store.__dict__.get("xml"))
    final_stat.addOption("text", store.__dict__.get("text"))

    PDFPath = []

    # On vérifie si le fichier a bien les droits de lecture ET d'écriture
    # Ajout de l'extension .pdf
    for file in listdir(pathDirectory):
        if os.access(os.path.join(pathDirectory, file), os.F_OK | os.R_OK | os.W_OK) and file[-4:] == ".pdf":
            PDFPath.append(os.path.join(pathDirectory, file))

    # Remove du dossier et son contenu
    if (os.path.exists(final_stat.output)):
        shutil.rmtree(final_stat.output)

    # Conversion en txt
    for path in PDFPath:
        # DEBUG ############
        # if not "METICS" in path:
        #    continue
        ####################
        print("Convert file " + path + "...")
        extraction.run(path, final_stat)


"""
Fonction qui détermine un affiche d'erreur de commande
"""


def errorUsage():
    print("Usage: irisa_parser.py <options> <inputDirectory>")
    print(exit)
    exit()
