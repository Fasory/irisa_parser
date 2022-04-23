import copy
from enum import Enum, unique
from math import floor
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTTextLineVertical, LTChar, LTTextLine, LTAnno

from text_contents.EnglishVocab import EnglishVocab

MAX_HEADER_HEIGHT = 70 #70
MAX_FOOTER_HEIGHT = 100 # si en fonction des marges: 25 # 80
HEADER_LEN_LIMIT = 150
FOOTER_LEN_LIMIT = 110

APPROX_EQ_LIMIT = 2

def approx_equal(x, y):
    print(abs(x-y))
    return abs(x - y) <= APPROX_EQ_LIMIT

def sort_y(contents_lst):
    contents_lst.sort(key=lambda c: c.position[1], reverse=True)

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

        self._top_margin_size = 0

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
            font_name = c.major_font
            font_size = c.major_font_size

            if font_name in self._fonts.keys():
                self._fonts[font_name] += 1
            else:
                self._fonts[font_name] = 0

            if font_size in self._font_sizes.keys():
                self._font_sizes[font_size] += 1
            else:
                self._font_sizes[font_size] = 0

        # La taille de la marge est le Y du content qui a le plus petit Y
        biggest_y_content = max(self._contents, key=lambda c: c.position[3])
        self._top_margin_size = self.height - biggest_y_content.position[3]

        self._major_font = max(self._fonts, key=self._fonts.get)
        self._major_font_size = round(max(self._font_sizes, key=self._font_sizes.get))


    @property
    def major_font(self):
        return self._major_font

    @property
    def major_font_size(self):
        return self._major_font_size

    def __add__(self, other):
        """ Adds a new TextContentResult to the list of contents """
        if not isinstance(other, TextContentResult):
            raise TypeError(
                "must be TextContentResult, not " + type(other).__name__)
        self._contents.append(other)
        return self

    def __repr__(self) -> str:
        s = "-----------PAGE-------------\n"
        s += f"{self._width}x{self._height}\n"
        s += f"Margin: {self._top_margin_size}\n"
        s += f"FONT: {self.major_font}: {self.major_font_size}\n"
        s += "**\nHEADER\n" + repr(self._header) + "\n\n"
        s += "FOOTER\n" + repr(self._footer) + "\n**\n\n"
        for c in self._contents:
            s += repr(c) + "\n"

        return s

    def __str__(self):
        s = "-----------PAGE-------------\n"
        s += f"{self._width}x{self._height}\n"
        s += f"Margin: {self._top_margin_size}\n"
        s += f"FONT: {self.major_font}: {self.major_font_size}\n"
        s += "**\nHEADER\n" + repr(self._header) + "\n\n"
        s += "FOOTER\n" + repr(self._footer) + "\n**\n\n"
        for c in self._contents:
            s += str(c) + "\n"

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

    def is_secondary(self, content):
        """Check if the content is an annotation or anything else that must NOT be restituted"""
        return content.major_font != self.major_font or content.major_font_size != self.major_font_size

    def delete_useless_contents(self):
        """Delete contents that must NOT be restituted (such as annotations)"""
        #print("PAGE FONT:", self.major_font)
        #print("PAGE FONT SIZE:", self.major_font_size)
        #print("=====SEC===========================")
        #print([c for c in self._contents if c.is_secondary(self.major_font, self.major_font_size)])
        #print("===================================")

        self._contents = [c for c in self._contents if not self.is_secondary(c)]

    def process_accents(self):
        for c in self._contents:
            c.process_accents()

    def is_header(self, content):
        return content.position[1] >= (self._height - MAX_HEADER_HEIGHT) and len(content) <= HEADER_LEN_LIMIT and content.is_short() and (content.starts_with_uppercase() or content.starts_with_number())

    def is_footer(self, content):
        # En bas de la page et commence par une majuscule
        if content.position[1] < MAX_FOOTER_HEIGHT and (content.starts_with_uppercase() or content.starts_with_number()) and len(content) <= FOOTER_LEN_LIMIT:
            return True

        return False

    def process_header_footer(self):
        new_contents = []

        # Footer
        to_remove = []
        # 1ers contents de la liste, qui sont en bas de la page
        i = 0
        while self._contents[i].position[3] <= MAX_FOOTER_HEIGHT:
            self._footer.append(self._contents[i])
            to_remove.append(i)

            i += 1

        # Les autres contents qui peuvent être en bas de la page
        while i < len(self._contents):
            c = self._contents[i]
            if self.is_footer(c):
                self._footer.append(c)
                to_remove.append(i)

            i += 1

        # Header
        i = 0
        while i < len(self._contents):
            # Si le content a déjà été rajouté dans footer, on ne s'en occupe pas
            if i not in to_remove:
                c = self._contents[i]

                if self.is_header(c):
                    self._header.append(c)
                else:
                    new_contents.append(c)

            i += 1

        self._contents = new_contents

    def is_centered(self, content):
        mid_x = self.width / 2
        content_center = content.get_center_x()
        print("center? ", end="")
        return approx_equal(mid_x, content_center)

    def is_on_left(self, content):
        mid_x = self.width / 2
        content_center = content.get_center_x()
        print("left? ", end="")
        return content_center <= mid_x

    def is_on_right(self, content):
        mid_x = self.width / 2
        content_center = content.get_center_x()
        print("right? ", end="")
        return content_center > mid_x

    # Si plus de la moitié des contents sont soit à gauche soit à droite du centre de la page, alors il y a 2 colonnes
    def count_columns(self):
        counter = 0
        for c in self._contents:
            print("...................")
            # Si le content est à gauche ou à droite du centre, on rajouter 1 au compteur
            if (not self.is_centered(c)) and (self.is_on_left(c) or self.is_on_right(c)):
                counter += 1
        
        if counter / len(self._contents) >= 0.5:
            return 2
        else:
            return 1

    def process_columns(self, nb_columns):
        if nb_columns == 2:
            # Séparation en 2 listes indépendantes
            left_contents = []
            right_contents = []
            for c in self._contents:
                if self.is_centered(c):
                    left_contents.append(c)
                elif self.is_on_right(c):
                    right_contents.append(c)
                # Par défaut, les contents sont mis à gauche (content qui sont pile au centre par ex)
                else:
                    left_contents.append(c)

            sort_y(left_contents)
            sort_y(right_contents)
            self._contents = left_contents + right_contents
        else:
            sort_y(self._contents)

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
        self._position = (min(elt.bbox[0], elt.bbox[2]), min(elt.bbox[1], elt.bbox[3]), max(elt.bbox[0], elt.bbox[2]),
                          max(elt.bbox[1], elt.bbox[3]))
        self._font_sizes = {}
        self._fonts = {}
        self._alignment = None
        self._first_font_size = None
        self._first_font = None

        lines_count = 0
        first_line = True
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
                if first_line:
                    self._first_font_size = line.size
                    self._first_font = line.fontname
                first_line = False
            elif isinstance(line, LTTextLine):
                for char in line:
                    if isinstance(char, LTChar):
                        if char.size not in self._font_sizes.keys():
                            self._font_sizes[char.size] = 0
                        self._font_sizes[char.size] += 1
                        if char.fontname not in self._fonts.keys():
                            self._fonts[char.fontname] = 0
                        self._fonts[char.fontname] += 1
                        if first_line:
                            if self._first_font_size == None and self._first_font == None:
                                self._first_font_size = char.size
                                self._first_font = char.fontname
                            elif self._first_font_size != char.size or self._first_font != char.fontname:
                                self._first_font_size = None
                                self._first_font = None
                                first_line = False
                first_line = False

        self._major_font = max(self._fonts, key=self._fonts.get)
        self._major_font_size = round(max(self._font_sizes, key=self._font_sizes.get))

        char_height = self.major_font_size
        self._line_spacing = (self.height - lines_count *
                              char_height) / (lines_count)

    @property
    def major_font(self):
        return self._major_font

    @property
    def major_font_size(self):
        return self._major_font_size

    def __len__(self):
        return len(self._string)

    def __contains__(self, word):
        return word in self._string

    def __repr__(self):
        return f"<F={repr(self.major_font)} FS={repr(self.major_font_size)}> {self._position} [{self.width}, {self.height}]\n{repr(self._string)}"

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

    def first_font_size(self):
        return self._first_font_size

    @property
    def first_font(self):
        return self._first_font

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

    @staticmethod
    def _check_word(word):
        return EnglishVocab.instance().check_word(word)

    def get_center_x(self):
        return (self.position[0] + self.position[2]) / 2

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
            .replace("ˆY", "Ŷ").replace("'y", "ý").replace("¨y", "ÿ").replace("`y", "ỳ").replace("ˆy", "ŷ")\
            .replace("ˇr", "ř").replace("ˇS", "Š")

    def starts_with_uppercase(self):
        return self._string.strip()[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def starts_with_number(self):
        return self._string.strip()[0] in "0123456789"

    def is_short(self):
        return len(self) <= HEADER_LEN_LIMIT

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
