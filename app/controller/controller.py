#!/usr/bin/python
"""
Le controleur permet de vérifier les entrées du programme par :
- La vérification de la syntaxe de la commande ;
- La vérification de l'existence & des permissions du dossier d'entrée ;
- La vérification du format & des permissions des fichiers d'entrées.

-- Input : String (commande)
-- Output : Fichier
"""

OUTPUT_DIR = "/out"
# Ce module donne accès à tous les arguments de ligne de commande
import sys
import os

def run():

def controler():
    # On vérifie qu'il n'y a qu'un seul et unique argument
    if len(sys.argv) != 2:
        print("Usage: irisa_parser.py <pathDirectory>")
        print(exit)
        exit()
    else:
        pathDirectory=sys.argv[1]
        # On vérifie si le répertoire/fichier entré existe
        if os.path.exists(pathDirectory)!=True:
            sys.exit("error -> <pathDirectory> does not exist")
        if not os.access(pathDirectory, os.F_OK | os.R_OK | os.W_OK):
            sys.exit("error -> you do not have write AND read permissions")
