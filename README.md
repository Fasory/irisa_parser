## Sommaire

1. Structure du readme
2. Explication générale du projet
3. Procédure de lancement
4. Commandes utiles et informations générales

## Explication générale du projet

Le but de ce projet est de créer un analyseur de texte pour le laboratoire IRISA. Celui-ci devra pouvoir tout d'abord convertir le fichier pdf en texte brut qui sera remis en forme par le programme pour être compréhensible par un outil de traitement automatique du langage.
Cet outil sera développé en python et la conversion pdf en format texte et xml sera faite à l'aide de la librairie python pdfminer.

## Procédure d'installations

### pdfminer :
* ```pip install pdfminer.six```

### spacy :
* ```pip install spacy```
* ```python -m spacy download en_core_web_sm```

### alive_progress (librairie progressbar)

* ```pip install alive_progress```

### inquirer (librairie menu)

* ```pip install inquirer```

## Procédure de lancement
```
python ./IRISA-Parser.py [-h] [-t] [-x] pathDirectory

positional arguments:
  
  pathDirectory       the path of the input folder containing the pdf files

optional arguments:

  -h, --help  show this help message and exit
  -t, --text  select plain text result format
  -x, --xml   select xml result format

```
  
