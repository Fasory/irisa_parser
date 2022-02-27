"""
Processing step
"""
import spacy

import restitution
from extraction.TextExtractionResult import TextAlignment
from .TextProcessingResult import TextProcessingResult
from processing.tools import largest_contents, top_content, closer_content, rm_multiple_spaces, clear_beginning_line


def run(result, target):
    restitution.run(TextProcessingResult(result.filename,
                                         find_title(result.pages),
                                         find_authors(result.pages),
                                         find_abstract(result.pages)), target)


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
        return "N/A"
    return title.string.replace("\n", " ") + "\n"


def find_authors(pages):
    """
    Return a string list of authors

    :param pages:
    :return:
    """
    authors = []
    if len(pages) == 0:
        return authors
    contents = pages[0].contents_higher()
    nlp = spacy.load("en_core_web_sm")
    for content in contents:
        # on analyse ligne par ligne chaque content
        for line in content.string.split("\n"):
            nb_words = len([elt for elt in line.split(" ") if elt != ""])
            doc = nlp(clear_beginning_line(line))
            # on détecte les noms
            names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
            nb_name_words = 0
            for name in names:
                nb_name_words += len([word for word in name.split(" ") if word != ""])
            # on n'analyse pas la suite du content si 50% des mots ne sont pas des noms
            if nb_words / 2 > nb_name_words:
                break
            authors += names
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
