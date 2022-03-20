import copy
from enum import Enum, unique
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTTextLineVertical, LTChar, LTTextLine, LTAnno

from text_contents.EnglishVocab import EnglishVocab


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

    def __add__(self, other):
        """ Adds a new TextContentResult to the list of contents """
        if not isinstance(other, TextContentResult):
            raise TypeError(
                "must be TextContentResult, not " + type(other).__name__)
        self._contents.append(other)
        return self

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

    def sort_y(self):
        self._contents.sort(key=lambda c: c.position[1], reverse=True)

    def merge_horizontal(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            merged = self._contents[i]
            first_pos = merged.position
            last_pos = first_pos
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_horizontal(self._contents[j + 1]):
                next = self._contents[j + 1]
                print("-----HORZ-----")
                print(merged)
                print("*******")
                print(next)
                print("--------------")
                merged = merged.merge_horizontal(next)
                last_pos = next.position

                j += 1

            merged.position = (
                first_pos[0],
                first_pos[1],
                last_pos[2],
                last_pos[3]
            )

            new_contents.append(merged)

            i = j + 1

        self._contents = new_contents


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

        #print(self._string, self._position)

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

        # TODO: on garde ça ?
        # Relcalcule largeur des caractères si encodage buggé (eg. Jing-cutepaste)
        # => si 1 seul caractère: width = font_size
        # if len(self._string) == 2 and self._string.endswith("\n") and self.width < char_height:
        #    x1 = self._position[0]
        #    y1 = self._position[1]
        #    x2 = self._position[2]
        #    y2 = self._position[3]

        #    x2 = x1 + char_height
        #    self._position = (x1, y1, x2, y2)

    def __str__(self):
        return f"{self._position} [{self.width}, {self.height}]\n{repr(self._string)}"

    def __repr__(self):
        return f"<{repr(self._string)}>"

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

    def is_near_horizontal(self, other):
        hd = self.hdistance(other)

        print("is_near", repr(self), repr(other),
              "fs:", self.major_font_size(),
              "dist:", hd)

        # Un caractère de haut et même police pour les 2 contents
        if self.height == self.major_font_size() and self.height == other.height\
                and self.major_font() == other.major_font():
            # Si se termine par un espace: on merge, car il y a forcément quelque chose après un espace
            if self._string.endswith(" ") or self._string.endswith(" \n")\
                    or hd <= self.major_font_size():
                return True

        return False

    def merge_horizontal(self, other):
        new = copy.deepcopy(self)

        self_s = new.string
        if self_s.endswith("\n") and len(self_s) == 2:
            self_s = self_s[0]
            print("new self_s", repr(self_s))

        other_s = other.string
        if other_s.endswith("\n") and len(other_s) == 2:
            other_s = other_s[0]
            print("new other_s", repr(other_s))

        new_s = self_s + other_s
        new_pos = (
            self.position[0], self.position[1],
            other.position[2], other.position[3]
        )

        new._string = new_s
        new._position = new_pos
        return new


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    UNDEFINED = 2
