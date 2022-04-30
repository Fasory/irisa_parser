"""
Processing step
"""
import spacy

import restitution
from extraction.TextExtractionResult import TextAlignment
from .TextProcessingResult import TextProcessingResult, Author
from processing.tools import largest_contents, top_content, closer_content, rm_multiple_spaces, clear_beginning_line, \
    hard_clear_line, percent_proper_names, under_contents, build_mail, build_real_authors, match, \
    research_match_by_first_letter, column_extraction, default_extraction
from .section import section_extraction, Section


def run(result, final_stat):
    text_processing_result = TextProcessingResult(result.filename)
    text_processing_result.title, content_title = find_title(result.pages)
    text_processing_result.authors = link_mails(find_authors(result.pages, content_title), find_mails(result.pages))
    text_processing_result.abstract, content_abstract = find_abstract(result.pages)
    section_extraction(result, text_processing_result, content_abstract, Section.INTRODUCTION, Section.REFERENCE)
    text_processing_result.references = find_references(result.pages)
    restitution.run(text_processing_result, final_stat)


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
    return title.string.replace("\n", " "), title


def find_authors(pages, title):
    """
    Return a author list of authors

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
    # var de récupération d'auteurs non reconnu
    skip_contents = []
    not_find = True
    authors_with_pos_y = []
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
                    or "institue" in lower_clear_line or "école" in lower_clear_line
                    or "school" in lower_clear_line or "college" in lower_clear_line):
                break
            # si au moins un nom a été détecté, on ajoute toute la ligne
            elif len(names) > 0 and (max_nb_names_in_line is None or len(words) < max_nb_names_in_line + 3):
                not_find = False
                authors_with_pos_y.append(round(max(content.position[1], content.position[3]), 5))
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
        if not_find:
            skip_contents.append(content)
        else:
            not_find = True
    # si on n'a aucun auteur, on retourne la liste de secours
    if not authors:
        authors = authors_assistance
    # sinon on complète la lsite des auteurs par en supposant que tous les contents à la même hauteur d'un content
    # reconnu comme auteur est considéré comme un auteur également
    else:
        for content in skip_contents:
            if round(max(content.position[1], content.position[3]), 5) in authors_with_pos_y:
                authors.append(hard_clear_line(content.string.split('\n')[0]).strip())
    # détection des couples (prénom, nom) des auteurs et transformation en liste d'objet Author
    return build_real_authors(authors)


def find_mails(pages):
    """
    Return a string list of mails

    :param pages:
    :return:
    """
    mails = []
    if len(pages) == 0:
        return mails
    contents = pages[0].contents_higher()
    for content in contents:
        # on part du principe que s'il y a un '@', le content possède forcément une adresse mail
        if '@' in content.string:
            lines = content.string.split('\n')
            # on recherche les lignes contenant '@'
            for i in range(len(lines)):
                if '@' in lines[i]:
                    # si c'est le 1er caractère, alors le début de l'adresse commence à la ligne précédente
                    if '@' == lines[i][0] and i > 0:
                        # si le mail continue sur la ligne suivante
                        if lines[i].strip()[-1] in ".-" and i < (len(lines) - 1):
                            mails += build_mail("".join([lines[i - 1], lines[i], lines[i + 1]]))
                        else:
                            mails += build_mail("".join([lines[i - 1], lines[i]]))
                    else:
                        # si le mail continue sur la ligne suivante
                        if lines[i].strip()[-1] in ".-" and i < (len(lines) - 1):
                            mails += build_mail("".join([lines[i], lines[i + 1]]))
                        else:
                            mails += build_mail(lines[i])
    return mails


def link_mails(authors, mails):
    """
    Return an author list of authors with the corresponding mail
    Check if we can find many authors in a same author name with mail linking

    :param authors:
    :param mails:
    :return:
    """
    if not mails:
        return authors
    new_authors = []
    mails_map = {}
    mails_linked = []
    for mail in mails:
        mails_map[mail.split('@')[0]] = mail
    for author in authors:
        current_author = None
        current_mail = None
        for word in author.name.split(" "):
            if current_author is not None or word[0] == word[0].upper():
                # recherche d'un mail qui match
                matched = match(word, mails_map.keys())
                # si on ne trouve pas un unique mail, on ajoute le mot à l'auteur courant
                if len(matched) != 1:
                    if current_author is None:
                        current_author = word
                    else:
                        current_author += " " + word
                # sinon
                else:
                    # s'il n'y a pas de mail courant
                    if current_mail is None:
                        current_mail = matched[0]
                        if current_author is None:
                            current_author = word
                        else:
                            current_author += " " + word
                    # sinon si le mail courant est identique à celui trouvé, on continue de contruire l'auteur courant
                    elif current_mail == matched[0]:
                        current_author += " " + word
                    # sinon c'est qu'on a trouvé deux auteurs en un nom, donc on ajoute l'auteur qu'on a fini de
                    # reconstruire et on construit le nom du nouvel auteur
                    else:
                        new_authors.append(Author(current_author,
                                                  None if current_mail is None else mails_map[current_mail]))
                        if current_mail is not None:
                            mails_linked.append(current_mail)
                        current_author = word
                        current_mail = None
        if current_author is not None:
            new_authors.append(Author(current_author,
                                      None if current_mail is None else mails_map[current_mail]))
            if current_mail is not None:
                mails_linked.append(current_mail)
    # dernière tentative d'assotiation pour les mails nom match
    for no_match in [elt for elt in mails_map.keys() if elt not in mails_linked]:
        new_authors = research_match_by_first_letter(no_match, new_authors, mails_map)
    return new_authors


def find_abstract(pages):
    """
    Return the string which contains the abstract of the article

    :param pages:
    :return:
    """
    if len(pages) == 0:
        return "N/A", None
    for content in pages[0].contents:
        # filtre les contenus uniquement horizontaux
        if content.alignment is TextAlignment.HORIZONTAL or content.alignment is None:
            # recherche basée sur le mot "abstract"
            if "abstract" in content.string[:15].lower():
                # cas où le titre de la section "Abstract" et le paragraphe sont dans le même content
                if len(content.string) > 15:
                    return content.string.replace("\n", " "), content
                # cas où le titre de la section "Abstract" et le paragraphe sont dans deux contents différents
                else:
                    abstract = closer_content(pages[0].contents, content).string
                    if abstract is None:
                        return "N/A", None
                    else:
                        return abstract.replace("\n", " "), content
            # recherche par formulation d'origine
            elif ("this article" in rm_multiple_spaces(content.string[:75]).lower() and
                  ("present" in content.string[12:75].lower() or "introduce" in content.string[12:75].lower())):
                return content.string.replace("\n", " "), content
    return "N/A", None


def find_references(pages):
    # Step 1, trouver la séction "References" sinon on retourne N/A
    target = None
    section = None
    for index in range(len(pages) - 1, -1, -1):
        for content in pages[index].contents:
            if "reference" in content.string[:25].lower():
                target = index
                section = content
                break
        if target is not None:
            break
    if target is None:
        return "N/A"
    # Step 2, on établit un étalon de référence ainsi que leur disposition
    pos = section.string[:-1].find('\n')
    # Cas où la première référence se trouve dans le même content que le titre de la section "References"
    if pos > -1:
        standard = section
        references = standard.string[pos+1:]
    else:
        standard = closer_content(pages[target].contents, section)
        if standard is None:
            return "N/A"
        references = standard.string
    # Step 3, extraction
    # Cas selon une disposition sans colonne
    if standard.position[0] < pages[target].width / 3 and pages[target].width * 2 / 3 < standard.position[2]:
        return default_extraction(references, standard, pages[target:]).replace('\n', " ")
    # Cas selon une disposition avec colonne
    else:
        return column_extraction(references, standard, pages[target:]).replace('\n', " ")
