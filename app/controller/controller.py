#!/usr/bin/python
"""
Le controleur permet de vérifier les entrées du programme par :
- La vérification de la syntaxe de la commande ;
- La vérification de l'existence & des permissions du dossier d'entrée ;
- La vérification du format & des permissions des fichiers d'entrées.

-- Input : String (commande)
-- Output : Fichier
"""

import app.extraction as extraction, sys, os, glob

OUTPUT_DIR = "/out"
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
    while (var.startswith('-')) :
        options.append(var)
        i+=1
        var = sys.argv[i]

    if options.count() == 0 :
        var = sys.argv[i+1] 

    if not var.count('/') :
        errorUsage()

    if(options.count()) :
        while options.count() != 0 :
            currentOption = options.pop()
            if currentOption == "-h" or currentOption == "--help" :
                print("") # Faire un message pour les options possibles
            """
            TO DO
            Options suivantes
            Penser à gérer aussi les -hdshqdabzd avec plusieurs lettres collées
            """   
    
    pathDirectory = var
    
    # On vérifie si le répertoire/fichier entré existe
    if os.path.exists(pathDirectory)!=True:
        sys.exit("error -> <pathDirectory> does not exist")
    if not os.access(pathDirectory, os.F_OK | os.R_OK | os.W_OK):
        sys.exit("error -> you do not have write AND read permissions")
    
    for file in glob.glob(pathDirectory + "*.pdf") :
        if not os.access(file, os.F_OK | os.R_OK | os.W_OK):
            sys.exit("error -> you do not have write AND read permissions")
            
    extraction.run(pathDirectory)

def errorUsage() :
    print("Usage: irisa_parser.py <options> <inputDirectory>")
    print(exit)
    exit()