"""
Utilities of processing step
"""
import re

from processing.TextProcessingResult import Author


def largest_contents(contents, alignment=None):
    """
    Returns a list of contents that have the largest font size

    :param alignment:
    :param contents:
    :return:
    """
    result_contents = []
    if len(contents) == 1:
        result_contents.append(contents[0])
    elif len(contents) > 1:
        result_contents.append(contents[0])
        for content in contents[1:]:
            if alignment is not None:
                if content.alignment != alignment:
                    continue
            if result_contents[0].major_font_size() == content.major_font_size():
                result_contents.append(content)
            elif result_contents[0].major_font_size() < content.major_font_size():
                result_contents = [content]
    return result_contents


def top_content(contents):
    """
    Return the content closest to the upper left corner of the list
    passed in parameter

    :param contents:
    :return:
    """
    if len(contents) == 0:
        return None
    elif len(contents) == 1:
        return contents[0]
    else:
        top = contents[0]
        for content in contents[1:]:
            if min(content.position[1], content.position[3]) < min(top.position[1], top.position[3]):
                top = content
            elif (min(content.position[1], content.position[3]) == min(top.position[1], top.position[3]) and
                  min(content.position[0], content.position[2]) < min(top.position[0], top.position[2])):
                top = content
        return top


def closer_content(contents, target):
    """
    Searches for the closest content in the same vertical alignment
    under the target

    :param contents:
    :param target:
    :return:
    """
    closer = None
    x, y = min(target.position[0], target.position[2]), min(target.position[1], target.position[3])

    for content in contents:
        if ((content.position[0] <= x <= content.position[2] or content.position[2] <= x <= content.position[0]) and
                max(content.position[1], content.position[3]) < y):
            if closer is None:
                closer = content
            elif max(closer.position[1], closer.position[3]) < max(content.position[1], content.position[3]):
                closer = content
    return closer


def rm_multiple_spaces(string):
    """
    Removes multiple spaces in a string

    :param string:
    :return:
    """
    return " ".join([word for word in string.split(" ") if word != ""])


def clear_beginning_line(line):
    words = [word for word in line.split(" ") if word != ""]
    checkpoint = 0
    for word in words:
        if word[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            return " ".join(words[checkpoint:])
        else:
            checkpoint += 1
    return ""


def hard_clear_line(line):
    # old regex : r'[A-Za-zÀ-ÿ0-9 .-]+'
    return "".join(re.findall(r'^[ ]*[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ.-]*|[,]?[ ]+[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ.-]*', line))


def basic_mail_section(section):
    return re.findall(r'[a-z0-9.-]+', section)


def percent_proper_names(words):
    if not words:
        return 0
    proper_name = 0
    ref = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for word in words:
        if len(word) > 1 and word[0] in ref:
            proper_name += 1
    return proper_name / len(words)


def under_contents(contents, reference):
    return [content for content in contents if min(reference.position[1], reference.position[3]) >
            max(content.position[1], content.position[3])]


def build_mail(mail_string):
    mails = []
    contents = mail_string.split('@')
    if len(contents) != 2:
        return mails
    section = basic_mail_section(contents[1])
    if len(section) != 1:
        return mails
    domain = section[0]
    section = basic_mail_section(contents[0])
    if len(section) < 1:
        return mails
    mail_ids = section
    for mail_id in mail_ids:
        mails.append(mail_id + '@' + domain)
    return mails


def build_real_authors(authors, always_real=False):
    real_authors = []
    if always_real:
        for author in authors:
            real_authors.append(Author(clear_name(author)))
    else:
        # on part du pricipe que s'il existe une quelconque marque de séparation différente d'un simple espace, alors
        # tous les auteurs ont une marque de séparation, sinon soit on a potentiellement à faire à une liste de noms
        # séparés indifférement des couples (prénom, nom) des autres auteurs par un simple espace ou soit c'est un seul
        # couple de (prénom, nom)
        explicit_mark = False
        # vérification de la séparation explicite pour traiter correctement les premiers auteur qui n'auraient pas
        # de séparaction alors que c'est explicite
        for author in authors:
            if ',' in author or " and " in author or "  " in author:
                explicit_mark = True
                break
        for author in authors:
            # si le " and " est présent, alors ce qui se trouve derrière le " and " est forcément un author
            sub_authors = author.split(" and ")
            if len(sub_authors) > 1:
                if len(sub_authors) == 2:
                    real_authors.append(Author(clear_name(sub_authors[1])))
                # cas où y a plus d'un " and ", donc on part du principe que c'est une erreur de détection d'auteurs
                else:
                    continue
            # on vérifie s'il y a une séparation par ',' ou par au moins un double espace, si c'est le cas, on suppose
            # que tous les auteurs sont séparés ainsi sur cette ligne
            if ',' in sub_authors[0]:
                for name in sub_authors[0].split(','):
                    if name:
                        real_authors.append(Author(clear_name(name)))
            elif "  " in sub_authors[0]:
                for name in sub_authors[0].split("  "):
                    if name:
                        real_authors.append(Author(clear_name(name)))
            elif explicit_mark:
                real_authors.append(Author(clear_name(sub_authors[0])))
            # cas de (prénom, nom) indéterminé
            else:
                real_authors.append(Author(clear_name(sub_authors[0])))
    return real_authors


def clear_name(name):
    words = name.split(' ')
    name = ""
    for word in words:
        if word and word[0] not in "0123456789":
            if not name:
                name = word
            else:
                name += " " + word
    return name


def match(token, targets):
    matched = []
    token = without_accent(token).lower()
    for unit in targets:
        if token in unit or token.split('-')[0] in unit:
            matched.append(unit)
    if not matched:
        for unit in targets:
            if unit in token:
                matched.append(unit)
    return matched


def research_match_by_first_letter(token, targets, dict_tokens):
    result = []
    size = len(token)
    for target in targets:
        words = without_accent(target.name).lower().split(" ")
        if len(words) < size:
            result.append(target)
        else:
            for i in range(len(words) - (size - 1)):
                buffer = ""
                for j in range(size):
                    buffer += words[i+j][0]
                if buffer == token:
                    words = target.name.split(" ")
                    result.append(Author(" ".join(words[i:(i+size)]), dict_tokens[token]))
                    result.append(Author(" ".join(words[:i] + words[(i+size):]), target.mail))
                    break
    return result


REF = {"Á": "A", "Ä": "A", "À": "A", "Â": "A", "á": "a", "ä": "a", "à": "a", "â": "a", "É": "E",
       "Ë": "E", "È": "E", "Ê": "E", "é": "e", "ë": "e", "è": "e", "ê": "e", "ç": "c", "Í": "I",
       "Ï": "I", "Ì": "I", "Î": "I", "í": "i", "ï": "i", "ì": "i", "î": "i", "Ó": "O", "Ö": "O",
       "Ò": "O", "Ô": "O", "ó": "o", "ö": "o", "ò": "o", "ô": "o", "Ú": "U", "Ü": "U", "Ù": "U",
       "Û": "U", "ú": "u", "ü": "u", "ù": "u", "û": "u", "Ý": "Y", "Ÿ": "Y", "Ỳ": "Y", "Ŷ": "Y",
       "ý": "y", "ÿ": "y", "ỳ": "y", "ŷ": "y"}


def without_accent(word):
    new_word = ""
    for c in word:
        if c in REF.keys():
            new_word += REF[c]
        else:
            new_word += c
    return new_word
