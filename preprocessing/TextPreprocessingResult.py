# -*-coding:utf-8 -*-

"""
This source file contains all the classes allowing
to give a representation of a file after the
pre-processing.
"""


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

        self.preprocess()
        self.compute_fonts()

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


    def preprocess(self):
        for p in self._pages:
            p.process_header_footer()
        
        # Compter les colonnes
        second_page = self._pages[1]
        nb_columns = second_page.count_columns()
        print("NB COL", nb_columns)
        for p in self._pages:
            p.process_columns(nb_columns)

        for p in self._pages:
            p.process_accents()

            self._contents += p.contents

    def print_result(self):
        print("APRES PREPROC\n")
        print("#####################", self._filename, "#####################")
        for p in self._pages:
            print(p)

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
