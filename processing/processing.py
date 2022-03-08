"""
Processing step
"""
import spacy

import restitution
from extraction.TextExtractionResult import TextAlignment
from .TextProcessingResult import TextProcessingResult
from processing.tools import largest_contents, top_content, closer_content, rm_multiple_spaces, clear_beginning_line, \
    hard_clear_line, percent_proper_names, under_contents


def run(result, final_stat):
    title, content_title = find_title(result.pages)
    authors = find_authors(result.pages, content_title)
    abstract = find_abstract(result.pages)
    references = find_references(result.pages)
    restitution.run(TextProcessingResult(result.filename, title, authors, abstract, references), final_stat)


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
            lower_clear_line = clear_line.lower()
            words = [word for word in clear_line.split(" ") if word != ""]
            # si le nombre de mots en majuscule est supérieur à 50%, ça vaut le coup de regarder le content
            percent = percent_proper_names(words)
            if percent < 0.5:
                break
            doc = nlp(clear_line)
            # on détecte les noms
            names = [ent.text.strip() for ent in doc.ents if ent.label_ == 'PERSON']
            # si la ligne contient un mot clef, elle est instantanément ignorée
            if ("laborato" in lower_clear_line or "universit" in lower_clear_line
                    or "department" in lower_clear_line or "département" in lower_clear_line
                    or "institue" in lower_clear_line):
                break
            # si au moins un nom a été détecté, on ajoute toute la ligne
            elif len(names) > 0 and (max_nb_names_in_line is None or len(words) < max_nb_names_in_line + 3):
                authors.append(clear_line)
                if max_nb_names_in_line is None:
                    max_nb_names_in_line = len(words)
                else:
                    max(max_nb_names_in_line, len(words))
            # si rien n'a été détecté comme nom, mais que 90% des mots sont en majuscule, on prend la ligne en secours
            elif percent > 0.9 and len(words) > 1 and (
                    max_nb_names_in_line is None or len(words) < max_nb_names_in_line + 3):
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
        if content.alignment is TextAlignment.HORIZONTAL or content.alignment is None:
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


def find_references(pages):
    # Step 1, trouver la séction "References"
    target = None
    for index in range(len(pages) - 1, -1, -1):
        for content in pages[index].contents:
            if "reference" in content.string[:15].lower():
                target = index
                break
        if target is not None:
            break
    # Step 2, extraire les références sur la page ciblé ainsi que les suivantes
    if target is None:
        return "N/A"
