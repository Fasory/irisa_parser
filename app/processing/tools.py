"""
Utilities of processing step
"""


def largest_contents(contents):
    """
    Returns a list of contents that have the largest font size

    :param contents:
    :return:
    """
    result_contents = []
    if len(contents) == 1:
        result_contents.append(contents[0])
    elif len(contents) > 1:
        result_contents.append(contents[0])
        for content in contents[1:]:
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
            if min(content.position()[1], content.position()[3]) < min(top.position()[1], top.position()[3]):
                top = content
            elif (min(content.position()[1], content.position()[3]) == min(top.position()[1], top.position()[3]) and
                  min(content.position()[0], content.position()[2]) < min(top.position()[0], top.position()[2])):
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
                min(content.position[1], content.position[3]) > y):
            if closer is None:
                closer = content
            elif min(closer.position[1], closer.position[3]) > min(content.position[1], content.position[3]):
                closer = content
    return closer


def rm_multiple_spaces(string):
    """
    Removes multiple spaces in a string

    :param string:
    :return:
    """
    return " ".join([word for word in string.split(" ") if word != ""])
