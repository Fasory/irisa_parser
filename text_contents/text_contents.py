import copy
from enum import Enum, unique
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTTextLineVertical, LTChar, LTTextLine, LTAnno

from text_contents.EnglishVocab import EnglishVocab

MAX_HEADER_HEIGHT = 80


class TextPageResult:
    """
    This class represents the extraction of a page from
    a file. It gathers the number of the extracted page
    and a list of its content.
    """

    def __init__(self, number, width, height):
        """ Constructor """
        if not isinstance(number, int):
            raise TypeError("must be int, not " + type(number).__name__)
        self._number = number
        self._contents = []
        self._width = width
        self._height = height
        self._fonts = {}
        self._font_sizes = {}

        self._footer = []
        self._header = []

    @property
    def number(self):
        """ Get page number """
        return self._number

    @property
    def contents(self):
        """ Get page content """
        return self._contents

    @property
    def width(self):
        """ Get width """
        return self._width

    @property
    def height(self):
        """ Get height """
        return self._height

    def compute_fonts(self):
        for c in self._contents:
            font_name = c.major_font()
            font_size = c.major_font_size()

            if font_name in self._fonts.keys():
                self._fonts[font_name] += 1
            else:
                self._fonts[font_name] = 0

            if font_size in self._font_sizes.keys():
                self._font_sizes[font_size] += 1
            else:
                self._font_sizes[font_size] = 0

    def major_font(self):
        return max(self._fonts, key=self._fonts.get)

    def major_font_size(self):
        return max(self._font_sizes, key=self._font_sizes.get)

    def __add__(self, other):
        """ Adds a new TextContentResult to the list of contents """
        if not isinstance(other, TextContentResult):
            raise TypeError(
                "must be TextContentResult, not " + type(other).__name__)
        self._contents.append(other)
        return self

    def __repr__(self) -> str:
        s = "-----------PAGE-------------\n"
        s += "**\nHEADER\n" + repr(self._header) + "\n\n"
        s += "FOOTER\n" + repr(self._footer) + "\n**\n\n"
        for c in self._contents:
            s += repr(c) + "\n"

        return s

    def first_content(self):
        return self._contents[0]

    def delete_first_content(self):
        self._contents.pop(0)

    def last_content(self):
        return self._contents[-1]

    def change_last_content(self, content):
        self._contents[-1] = content

    def contents_higher(self):
        proper = []
        limit = self._height / 2
        for content in self._contents:
            if max(content.position[1], content.position[3]) >= limit:
                proper.append(content)
        return proper

    def contents_lower(self):
        proper = []
        limit = self._height / 2
        for content in self._contents:
            if max(content.position[1], content.position[3]) < limit:
                proper.append(content)
        return proper

    def process_accents(self):
        for c in self._contents:
            c.process_accents()

    def process_header_footer(self):
        new_contents = []

        # Footer
        to_remove = []
        # 1ers contents de la liste, qui sont en bas de la page
        i = 0
        while self._contents[i].position[3] < MAX_HEADER_HEIGHT:
            self._footer.append(self._contents[i])
            to_remove.append(i)

            i += 1

        # Les autres contents qui peuvent être en bas de la page
        while i < len(self._contents):
            c = self._contents[i]
            if c.is_footer(self.major_font(), self.major_font_size()):
                self._footer.append(c)
                to_remove.append(i)
            else:
                new_contents.append(c)

            i += 1

        # Header
        i = 0
        while i < len(self._contents):
            # Si le content a déjà été rajouté dans footer, on ne s'en occupe pas
            if i not in to_remove:
                c = self._contents[i]

                if c.is_header():
                    self._header.append(c)
                else:
                    new_contents.append(c)

            i += 1

        self._contents = new_contents

    def sort_y(self):
        self._contents.sort(key=lambda c: c.position[1], reverse=True)


class TextContentResult:
    """
    This class represents a targeted data block of a file.
    It is characterized by a character string, a list of
    used fonts, a list of used size and the position of
    the block on the page from which it comes.
    """

    def __init__(self, elt):
        """ Constructor """
        if not isinstance(elt, LTTextContainer):
            raise TypeError("must be LTTextContainer, not " +
                            type(elt).__name__)
        self._container = elt
        self._string = elt.get_text()
        self._position = elt.bbox
        self._font_sizes = {}
        self._fonts = {}
        self._alignment = None

        # print(self._string, self._position)

        lines_count = 0
        for line in elt:
            if not isinstance(line, LTAnno):
                lines_count += 1

            # define alignment
            if isinstance(line, LTTextLineHorizontal):
                if self._alignment is None:
                    self._alignment = TextAlignment.HORIZONTAL
                elif self._alignment is TextAlignment.VERTICAL:
                    self._alignment = TextAlignment.UNDEFINED
            elif isinstance(line, LTTextLineVertical):
                if self._alignment is None:
                    self._alignment = TextAlignment.VERTICAL
                elif self._alignment is TextAlignment.HORIZONTAL:
                    self._alignment = TextAlignment.UNDEFINED
            if isinstance(line, LTChar):
                if line.size not in self._font_sizes.keys():
                    self._font_sizes[line.size] = 0
                self._font_sizes[line.size] += 1
                if line.fontname not in self._fonts.keys():
                    self._fonts[line.fontname] = 0
                self._fonts[line.fontname] += 1
            elif isinstance(line, LTTextLine):
                for char in line:
                    if isinstance(char, LTChar):
                        if char.size not in self._font_sizes.keys():
                            self._font_sizes[char.size] = 0
                        self._font_sizes[char.size] += 1
                        if char.fontname not in self._fonts.keys():
                            self._fonts[char.fontname] = 0
                        self._fonts[char.fontname] += 1

        char_height = self.major_font_size()
        self._line_spacing = (self.height - lines_count *
                              char_height) / (lines_count)

    def __repr__(self):
        return f"{self._position} [{self.width}, {self.height}]\n{repr(self._string)}"

    def __str__(self):
        return f"-----------\n{self._string}-----------"

    def hdistance(self, other_content):
        return self._container.hdistance(other_content.container)

    def vdistance(self, other_content):
        return self._container.vdistance(other_content.container)

    @property
    def container(self):
        return self._container

    @property
    def width(self):
        return abs(self.position[0] - self.position[2])

    @property
    def height(self):
        return self._container.height

    @property
    def string(self):
        """ Get raw string of content """
        return self._string

    @property
    def position(self):
        """ Get position of content """
        return self._position

    @position.setter
    def position(self, pos):
        """Change the position of the content"""
        self._position = pos

    @property
    def font_sizes(self):
        """ Get dictionnary of font sizes """
        return self._font_sizes

    @property
    def fonts(self):
        """ Get dictionnary of fonts """
        return self._fonts

    @property
    def alignment(self):
        """ Get alignment """
        return self._alignment

    def major_font(self):
        return max(self._fonts, key=self._fonts.get)

    def major_font_size(self):
        return max(self._font_sizes, key=self._font_sizes.get)

    @staticmethod
    def _check_word(word):
        return EnglishVocab.instance().check_word(word)

    def process_accents(self):
        self._string = self._string.replace("´A", "Á").replace("¨A", "Ä").replace("`A", "À").replace("ˆA", "Â")\
            .replace("´a", "á").replace("¨a", "ä").replace("`a", "à").replace("ˆa", "â").replace("´E", "É")\
            .replace("¨E", "Ë").replace("`E", "È").replace("ˆE", "Ê").replace("´e", "é").replace("¨e", "ë")\
            .replace("`e", "è").replace("ˆe", "ê").replace("c¸", "ç").replace("'I", "Í").replace("¨I", "Ï")\
            .replace("`I", "Ì").replace("ˆI", "Î").replace("´ı", "í").replace("¨ı", "ï").replace("`ı", "ì")\
            .replace("ˆı", "î").replace("'O", "Ó").replace("¨O", "Ö").replace("`O", "Ò").replace("ˆO", "Ô")\
            .replace("'o", "ó").replace("¨o", "ö").replace("`o", "ò").replace("ˆo", "ô").replace("'U", "Ú")\
            .replace("¨U", "Ü").replace("`U", "Ù").replace("ˆU", "Û").replace("'u", "ú").replace("¨u", "ü")\
            .replace("`u", "ù").replace("ˆu", "û").replace("'Y", "Ý").replace("¨Y", "Ÿ").replace("`Y", "Ỳ")\
            .replace("ˆY", "Ŷ").replace("'y", "ý").replace("¨y", "ÿ").replace("`y", "ỳ").replace("ˆy", "ŷ")

    def starts_with_uppercase(self):
        return self._string[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def is_short(self):
        return False

    def is_header(self):
        return False

    def is_footer(self, page_major_font, page_major_font_size):
        # En bas de la page et commence par une majuscule
        if self.position[3] < MAX_HEADER_HEIGHT and self.starts_with_uppercase():
            # Police ou taille différente du reste de la page
            if (self.major_font() != page_major_font) or (self.major_font_size() != page_major_font_size):
                return True

        return False

    def vertical_merge(self, other, splitted_word=False):
        new = copy.deepcopy(self)
        new._string += other.string
        new._position = (
            other.position[0], other.position[1],
            self._position[2], self._position[3]
        )

        return new


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    UNDEFINED = 2
