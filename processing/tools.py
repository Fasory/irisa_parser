"""
Utilities of processing step
"""
import re


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
    x, y = target.position[0], target.position[3]
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
    return "".join(re.findall(r'[A-Za-zÀ-ÿ0-9 .-]+', line))


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
