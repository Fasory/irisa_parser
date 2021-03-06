# -*-coding:utf-8 -*-
from text_contents.EnglishVocab import EnglishVocab

"""
This source file contains all the classes allowing
to give a representation of a file after the
pre-processing.
"""

TITLE_LEN_LIMIT = 50

def starts_with_uppercase(s):
    try:
        return s.strip()[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    except IndexError:
        return False

def starts_with_number(s):
    try:
        return s.strip()[0] in "0123456789"
    except IndexError:
        return False

def string_is_title(s):
    return len(s) <= TITLE_LEN_LIMIT and (starts_with_uppercase(s) or starts_with_number(s)) and EnglishVocab.instance().check_no_proper_name(s)

class TextPreprocessingResult:
    """
    Represent the pre-processing result. It stores the content,
    as TextExtractionResult.
    """

    def __init__(self, filename, pages):
        """Initializes the pre-processing result"""
        self._filename = filename
        self._pages = pages
        self._major_font = None
        self._major_font_size = None

        self._contents = []

        self.compute_fonts()
        self.preprocess()


    def compute_fonts(self):
        fonts = {}
        font_sizes = {}
        for p in self._pages:
            font_name = p.major_font
            font_size = p.major_font_size

            if font_name in fonts.keys():
                fonts[font_name] += 1
            else:
                fonts[font_name] = 0

            if font_size in font_sizes.keys():
                font_sizes[font_size] += 1
            else:
                font_sizes[font_size] = 0

        self._major_font = max(fonts, key=fonts.get)
        self._major_font_size = max(font_sizes, key=font_sizes.get)


    def process_accents(self):
        for c in self._contents:
            c.process_accents()


    def is_title_content(self, content):
        return string_is_title(content.string) and (content.major_font != self.major_font or content.major_font_size != self.major_font_size)

    def separate_titles(self):
        new_contents = []
        for c in self._contents:
            #print("********* SPLIT **********")
            if c.must_split():
                #print("====")

                c1, c2 = c.split()
                #print(repr(c1))
                #print(c1.is_title)
                #print("---")
                #print(repr(c2))

                new_contents.append(c1)
                new_contents.append(c2)
            else:
                new_contents.append(c)

        self._contents = new_contents

    def vertical_merge(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            merged = self._contents[i]
            first_pos = merged.position
            last_pos = first_pos
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_vertical(self._contents[j + 1], self._pages[0].height):
                next = self._contents[j + 1]
                merged.vertical_merge(next)
                last_pos = next.position

                j += 1

            merged.position = (
                last_pos[0],
                last_pos[1],
                first_pos[2],
                first_pos[3]
            )

            new_contents.append(merged)

            i = j + 1

        self._contents = new_contents

    def preprocess(self):
        for p in self._pages:
            p.vertical_merge()
            p.process_footer(self._major_font, self._major_font_size)
            if p.number > 1:
                p.process_columns()

            self._contents += p.contents

        self.process_accents()

        # S??paration titre - texte avant
        self.separate_titles()

        self.vertical_merge()


    def preprocess2(self, debug=False):
        for p in self._pages:
            p.vertical_merge()
            p.process_footer(self._major_font, self._major_font_size, debug)
            p.process_header(self._major_font, self._major_font_size, debug)
            if p.number > 1:
                p.process_columns()

            self._contents += p.contents

        self.process_accents()

        # S??paration titre - texte avant
        self.separate_titles()

        self.vertical_merge()


    def print_pages(self):
        print("APRES PREPROC: pages\n")
        print("#####################", self._filename, "#####################")
        for p in self._pages:
            print(p)

    def repr_pages(self):
        print("APRES PREPROC: pages\n")
        print("#####################", self._filename, "#####################")
        for p in self._pages:
            print(repr(p))

    
    def print_result(self):
        print("APRES PREPROC: contents\n")
        print("#####################", self._filename, "#####################")
        for c in self._contents:
            print(c)

    def repr_result(self):
        print("APRES PREPROC: contents\n")
        print("#####################", self._filename, "#####################")
        for c in self._contents:
            print(repr(c))

    @property
    def filename(self):
        """Get PDF file name"""
        return self._filename

    @property
    def pages(self):
        """Get the pages"""
        return self._pages

    @property
    def contents(self):
        """Get the contents"""
        return self._contents

    @property
    def major_font(self):
        """Get the major font name"""
        return self._major_font

    @property
    def major_font_size(self):
        """Get the major font size"""
        return self._major_font_size
