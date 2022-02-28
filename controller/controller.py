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

import extraction
import glob
import os
import sys

# Ce module donne accès à tous les arguments de ligne de commande


def run():
    controler()


def controler():
    # On vérifie qu'il n'y a qu'un seul et unique argument
    if len(sys.argv) != 2:
        errorUsage()
    i = 1
    options = []
    var = sys.argv[i]

    """
    while (var.startswith('-')):
        options.append(var)
        i += 1
        var = sys.argv[i]

    if len(options) == 0:
        var = sys.argv[i + 1]

    if not var.count('/'):
        errorUsage()

    if (options.count()):
        while options.count() != 0:
            currentOption = options.pop()
            if currentOption == "-h" or currentOption == "--help":
                print("test")  # Faire un message pour les options possibles
    """
    pathDirectory = var

    # On vérifie si le répertoire/fichier entré existe
    if os.path.exists(pathDirectory) != True:
        sys.exit("error -> <pathDirectory> does not exist")
    if not os.access(pathDirectory, os.F_OK | os.R_OK | os.W_OK):
        sys.exit("error -> you do not have write AND read permissions")

    PDFPath = []

    for file in listdir(pathDirectory):
        if os.access(os.path.join(pathDirectory, file), os.F_OK | os.R_OK | os.W_OK) and file[-4:] == ".pdf":
            PDFPath.append(os.path.join(pathDirectory, file))

    OUTPUT_DIR = os.path.join(pathDirectory, "out")
    if (os.path.exists(OUTPUT_DIR)):
        shutil.rmtree(OUTPUT_DIR)

    for path in PDFPath:
        # DEBUG ############
        # if not "METICS" in path:
        #    continue
        ####################
        print("Convert file " + path + "...")
        extraction.run(path, OUTPUT_DIR)


def errorUsage():
    print("Usage: irisa_parser.py <options> <inputDirectory>")
    print(exit)
    exit()
