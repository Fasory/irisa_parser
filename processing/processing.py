"""
Processing step
"""
import spacy

import restitution
from extraction.TextExtractionResult import TextAlignment
from .TextProcessingResult import TextProcessingResult
from processing.tools import largest_contents, top_content, closer_content, rm_multiple_spaces, clear_beginning_line, \
    hard_clear_line, percent_proper_names, under_contents


def run(result, target):
    title, content_title = find_title(result.pages)
    authors = find_authors(result.pages, content_title)
    abstract = find_abstract(result.pages)
    restitution.run(TextProcessingResult(result.filename, title, authors, abstract), target)


def find_title(pages):
    """
    Return the string which contains the title of the article

    :param pages:
    :return:
    """
    if len(pages) == 0:
        return "N/A"
    title = top_content(largest_contents(pages[0].contents_higher(), TextAlignment.HORIZONTAL))
    if title is None:
        return "N/A", None
    return title.string.replace("\n", " ") + "\n", title


def find_authors(pages, title):
    """
    Return a string list of authors

    :param title:
    :param pages:
    :return:
    """
    authors = []
    # liste de secours avec une moins bonne précision
    authors_assistance = []
    if len(pages) == 0:
        return authors
    contents = pages[0].contents_higher()
    if title is not None:
        contents = under_contents(contents, title)
    nlp = spacy.load("en_core_web_sm")
    for content in contents:
        # on analyse ligne par ligne chaque content
        max_nb_names_in_line = None
        for line in content.string.split("\n"):
            clear_line = hard_clear_line(line).strip()
            words = [word for word in clear_line.split(" ") if word != ""]
            # si le nombre de mots en majuscule est supérieur à 50%, ça vaut le coup de regarder le content
            percent = percent_proper_names(words)
            if percent < 0.5:
                break
            doc = nlp(clear_line)
            # on détecte les noms
            names = [ent.text.replace("\\", "").replace("∗", "").strip() for ent in doc.ents if ent.label_ == 'PERSON'
                     and "laborato" not in ent.text.lower() and "universit" not in ent.text.lower()]
            # si au moins un nom a été détecté, on ajoute toute la ligne
            if len(names) > 0 and (max_nb_names_in_line is None or len(words) < max_nb_names_in_line + 3):
                authors.append(clear_line)
                if max_nb_names_in_line is None:
                    max_nb_names_in_line = len(words)
                else:
                    max(max_nb_names_in_line, len(words))
            # si rien n'a été détecté comme nom, mais que 90% des mots sont en majuscule, on prend la ligne en secours
            elif percent > 0.9 and (max_nb_names_in_line is None or len(words) < max_nb_names_in_line + 3):
                authors_assistance.append(clear_line)
                if max_nb_names_in_line is None:
                    max_nb_names_in_line = len(words)
                else:
                    max(max_nb_names_in_line, len(words))
            # sinon on ignore le content
            else:
                break
    # si on n'a aucun auteur, on retourne la liste de secours
    if not authors:
        return authors_assistance
    return authors


def find_abstract(pages):
    """
    Return the string which contains the abstract of the article

    :param pages:
    :return:
    """
    if len(pages) == 0:
        return "N/A"
    for content in pages[0].contents:
        # filtre les contenus uniquement horizontaux
        if content.alignment is TextAlignment.HORIZONTAL:
            # recherche basée sur le mot "abstract"
            if "abstract" in content.string[:15].lower():
                # cas où le titre de la section "Abstract" et le paragraphe sont dans le même content
                if len(content.string) > 15:
                    return content.string.replace("\n", " ") + "\n"
                # cas où le titre de la section "Abstract" et le paragraphe sont dans deux contents différents
                else:
                    abstract = closer_content(pages[0].contents, content).string
                    if abstract is None:
                        return "N/A"
                    else:
                        return abstract.replace("\n", " ") + "\n"
            # recherche par formulation d'origine
            elif ("this article" in rm_multiple_spaces(content.string[:75]).lower() and
                  ("present" in content.string[12:75].lower() or "introduce" in content.string[12:75].lower())):
                return content.string.replace("\n", " ") + "\n"
    return "N/A"
