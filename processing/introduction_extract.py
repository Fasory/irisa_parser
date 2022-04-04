from text_contents import TextContentResult


def run(preprocess, cursor):
    introduction = ""
    for content in preprocess.contents[cursor:] :
        if laSuperMethodeDeClement(content, preprocess.majorbidule):
            break
        else :
            introduction += content.string
        cursor += 1
    return introduction, cursor
