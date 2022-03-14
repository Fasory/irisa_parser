## Sommaire

1. Structure du readme
2. Explication générale du projet
3. Procédure de lancement
4. Commandes utiles et informations générales

## Explication générale du projet

Le but de ce projet est de créer un analyseur de texte pour le laboratoire IRISA. Celui-ci devra pouvoir tout d'abord convertir le fichier pdf en texte brut qui sera remis en forme par le programme pour être compréhensible par un outil de traitement automatique du langage.
Cet outil sera développé en --, la conversion pdf en format texte sera faite à l'aide de la librairie python pdftotext.

## Procédure d'installastions

###pdfminer :
* ```pip install pdfminer.six```

###spacy :
* ```pip install spacy```
* ```python -m spacy download en_core_web_sm```

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
  

## Aide mémoire

####  _Commandes Git_
```git
Pour créer une branche :
	git checkout -d <nom de la branche>

Pour se déplacer sur une autre branche :
	git checkout <nom de la branche>

Pour ajouter de nouveaux fichiers au git (lorsque vous en créez) :
	git add -A 
Pour enregistrer vos modifications :
	git commit -a 
	 -> Normalement un éditeur de texte s'ouvre dans le terminal et il faut 	
	 rentrer un message résumant vos modifications

Pour valider vos modifications sur le projet gitlab distant :
	git push

Pour supprimer une branche :
	git branch -d <nom de la branche>
```

