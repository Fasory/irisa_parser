def run(contents, cursor):
    conclusion = ""
    for content in contents[cursor:] :
        if laSuperMethodeDeClement(content.string) :
            break
        else :
            conclusion += content.string
        cursor += 1
    return conclusion, cursor