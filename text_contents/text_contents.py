import copy
from enum import Enum, unique
import re

from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTTextLineVertical, LTChar, LTTextLine, LTAnno

from text_contents.EnglishVocab import EnglishVocab

MAX_HEADER_HEIGHT = 70 #70
MAX_FOOTER_HEIGHT = 100 # si en fonction des marges: 25 # 80
HEADER_LEN_LIMIT = 150
FOOTER_LEN_LIMIT = 80
FOOTER_LEN_LIMIT_SHORTEST = 50 # 50

TITLE_LEN_LIMIT = 50

APPROX_EQ_LIMIT = 10

TITLE_DIGIT_REGEX = r"[IVXLDCM0-9]"
TITLE_NO_REGEX = re.compile(TITLE_DIGIT_REGEX + r"+(\." + TITLE_DIGIT_REGEX + r"+)*(\.)?")

TITLES = ["abstract", "introduction", "acknowledgement", "acknowledgment", "conlusion", "discussion", "references"]

def approx_equal(x, y, lim=APPROX_EQ_LIMIT):
    return abs(x - y) <= lim

def sort_y(contents_lst):
    contents_lst.sort(key=lambda c: c.position[1], reverse=True)

def sort_x(contents_lst):
    contents_lst.sort(key=lambda c: c.position[0])


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

def string_is_title(s, debug=False):
    if debug:
        print(repr(s))
        print("****")
        print("regex = ", TITLE_NO_REGEX.match(s))
        print("mot titre = ", any(s.lower().startswith(t) for t in TITLES))
        print("UN = ",  starts_with_number(s) or starts_with_uppercase(s))
        print("Word = ", EnglishVocab.instance().check_no_proper_name(s))
        print("whole = ", len(s) <= TITLE_LEN_LIMIT and (TITLE_NO_REGEX.match(s) is not None) and (not any(s.lower().startswith(t) for t in TITLES)) and (starts_with_uppercase(s) or starts_with_number(s)) and EnglishVocab.instance().check_no_proper_name(s))

    # Il faut forcément respecter la taille limite
    if len(s) > TITLE_LEN_LIMIT:
        return False

    # Si commence par un titre (introduction, abstract, acknwoledgments, ...) => True
    if any(s.lower().startswith(t) for t in TITLES):
        return True

    # Si commence par un numéro de titre (1.2....) => True
    if TITLE_NO_REGEX.match(s) is not None:
        return True

    return (starts_with_uppercase(s) or starts_with_number(s)) and\
        EnglishVocab.instance().check_no_proper_name(s)


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
        s = f"-----------PAGE {self.number} -------------\n"
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

    def remove_contents(self, contents_to_remove):
        for c in contents_to_remove:
            self._contents.remove(c)

    def is_secondary(self, content):
        """Check if the content is an annotation or anything else that must NOT be restituted"""
        return content.major_font != self.major_font or content.major_font_size != self.major_font_size

    @staticmethod
    def is_in_major_font(content, doc_major_font, doc_major_size):
        #print("MF: ", self.major_font, ", F: ", content.major_font)
        #print("MS: ", self.major_font_size, ", S: ", content.major_font_size)
        return content.major_font == doc_major_font and content.major_font_size == doc_major_size



    def delete_useless_contents(self):
        """Delete contents that must NOT be restituted (such as annotations)"""
        #print("PAGE FONT:", self.major_font)
        #print("PAGE FONT SIZE:", self.major_font_size)
        #print("=====SEC===========================")
        #print([c for c in self._contents if c.is_secondary(self.major_font, self.major_font_size)])
        #print("===================================")

        self._contents = [c for c in self._contents if not self.is_secondary(c)]


    def vertical_merge(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            merged = self._contents[i]
            first_pos = merged.position
            last_pos = first_pos
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_vertical(self._contents[j + 1], self._height):
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


    def is_header(self, content, len_limit, doc_major_size, debug=False):
        start_un = content.starts_with_uppercase() or content.starts_with_number()

        return start_un and\
            not string_is_title(content.string, debug) and\
            content.has_short_height(doc_major_size) and\
            content.is_short(len_limit) and\
            (
                content.is_less_than_major_size(doc_major_size) or\
                content.is_in_major_size(doc_major_size)
            )

    def is_footer(self, content, len_limit, doc_major_font, doc_major_size, debug=False):
        if debug:
            print(repr(content))
            print("len = ", len(content), ", short ? ", content.is_short(len_limit))
            print("height = ", content.height, ", 2*MFS= ", 2 * doc_major_size)
            print("major = ", TextPageResult.is_in_major_font(content, doc_major_font, doc_major_size))
            print("whole cond = ", (content.starts_with_uppercase() or content.starts_with_number()) and (content.is_short(len_limit) or not TextPageResult.is_in_major_font(content, doc_major_font, doc_major_size)) and content.has_short_height(doc_major_size))

        # Si respecte le pattern "NuméroPage\nTexte", vrai
        if content.matches_footer_pattern():
            return True

        # En bas de la page et commence par une majuscule
        if (content.starts_with_uppercase() or content.starts_with_number()) and (content.is_short(len_limit) or not TextPageResult.is_in_major_font(content, doc_major_font, doc_major_size)) and content.has_short_height(doc_major_size):
            return True

        return False

    def same_y(self, content):
        return [c for c in self._contents if c.is_voverlap(content)]

    def process_footer(self, doc_major_font, doc_major_size, debug=False):
        if debug:
            print(f"************PROC FOOTER PAGE {self.number}***************\n")

        while True:
            # Récupère les contents en bas de la page
            lowest_content = min(self._contents, key=lambda c: c.position[1])
            low_contents = self.same_y(lowest_content)

            # Si moins d'1 content en bas, ou plus de 2, fin
            len_c = len(low_contents)
            if len_c not in [1, 2]:
                break

            if debug:
                print(f"------------- {len_c} contents -------------------")

            if len_c == 1:
                self.is_footer(low_contents[0], FOOTER_LEN_LIMIT, doc_major_font, doc_major_size, debug)
            if len_c == 2:
                self.is_footer(low_contents[0], FOOTER_LEN_LIMIT_SHORTEST, doc_major_font, doc_major_size, debug)
                if debug:
                    print("=======")
                self.is_footer(low_contents[1], FOOTER_LEN_LIMIT_SHORTEST, doc_major_font, doc_major_size, debug)

            # Si 2 contents: tous les 2 très courts
            cond_2_contents = len_c == 2 and all(self.is_footer(c, FOOTER_LEN_LIMIT_SHORTEST, doc_major_font, doc_major_size) for c in low_contents)

            # Si 1 content: moins court
            cond_1_content = len_c == 1 and self.is_footer(low_contents[0], FOOTER_LEN_LIMIT, doc_major_font, doc_major_size)

            # Arrête si on dépasse le quart de la page OU si une des 2 conditions précédentes sont pas respectées
            if (lowest_content.position[1] > (self._height / 4) or (not cond_1_content and not cond_2_contents)):
                break

            # Ajoute au footer après verif
            self._footer += low_contents

            self.remove_contents(low_contents) # Supprime tous les contents du bas de la page

    def process_header(self, doc_major_font, doc_major_size, debug=False):
        if debug:
            print(f"************PROC HEADER PAGE {self.number}***************\n")

        while True:
            # Récupère les contents en bas de la page
            highest_content = max(self._contents, key=lambda c: c.position[3])
            high_contents = self.same_y(highest_content)

            # Si moins d'1 content en bas, ou plus de 2, fin
            len_c = len(high_contents)
            if len_c not in [1, 2]:
                break

            if debug:
                print(f"------------- {len_c} contents -------------------")

            if len_c == 1:
                self.is_header(high_contents[0], FOOTER_LEN_LIMIT, doc_major_size, debug)
            if len_c == 2:
                self.is_header(high_contents[0], FOOTER_LEN_LIMIT_SHORTEST, doc_major_size, debug)
                if debug:
                    print("=======")
                self.is_header(high_contents[1], FOOTER_LEN_LIMIT_SHORTEST, doc_major_size, debug)

            # Si 2 contents: tous les 2 très courts
            cond_2_contents = len_c == 2 and all(self.is_header(c, FOOTER_LEN_LIMIT_SHORTEST, doc_major_size) for c in high_contents)

            # Si 1 content: moins court
            cond_1_content = len_c == 1 and self.is_header(high_contents[0], FOOTER_LEN_LIMIT, doc_major_size)

            # Arrête si on dépasse les 3/4 quarts de la page OU si une des 2 conditions précédentes sont pas respectées
            if (highest_content.position[1] < (self._height * 3 / 4) or (not cond_1_content and not cond_2_contents)):
                break

            # Ajoute au header après verif
            self._header += high_contents

            self.remove_contents(high_contents) # Supprime tous les contents du haut de la page


    def is_centered(self, content, debug=False):
        mid_x = self.width / 2
        content_center = content.get_center_x()
        if debug:
            print(f"CENTER: page mid ({mid_x}) == content mid ({content_center}) ? ", approx_equal(mid_x, content_center, 20))
        return approx_equal(mid_x, content_center, 20)

    def is_on_left(self, content, debug=False):
        mid_x = self.width / 2
        content_center = content.get_center_x()
        if debug:
            print(f"LEFT: content mid ({content_center}) <= page mid ({mid_x}) ? ", content_center <= mid_x)
        return content_center <= mid_x

    def is_on_right(self, content, debug=False):
        mid_x = self.width / 2
        content_center = content.get_center_x()
        if debug:
            print(f"RIGHT: content mid ({content_center}) > page mid ({mid_x}) ? ", content_center > mid_x)
        return content_center > mid_x

    def process_columns(self, debug=False):
        if debug:
            print(f"************ COLUMNS PAGE {self.number} ********************")
        # Séparation en 2 listes indépendantes
        left_contents = []
        right_contents = []
        for c in self._contents:
            if debug:
                print("------------")
                print(repr(c))
                print("===")
                self.is_centered(c, True)
                self.is_on_right(c, True)
                self.is_on_left(c, True)

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


class TextContentResult:
    """
    This class represents a targeted data block of a file.
    It is characterized by a character string, a list of
    used fonts, a list of used size and the position of
    the block on the page from which it comes.
    """

    footer_regex = re.compile(r"[0-9]+\n[A-Za-z_\ ]+")

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
        self._font_size_of_first_chars = {}
        self._font_of_first_chars = {}
        nb_limit_chars = 15
        nb_chars = 0

        self._is_title = False

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
                if first_line:
                    self._font_size_of_first_chars[line.size] = 1
                    self._font_of_first_chars[line.fontname] = 1
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
                            if self._first_font_size is None and self._first_font is None:
                                self._first_font_size = char.size
                                self._first_font = char.fontname
                            elif self._first_font_size != char.size or self._first_font != char.fontname:
                                self._first_font_size = None
                                self._first_font = None
                                first_line = False
                        if nb_chars < nb_limit_chars:
                            if char.size not in self._font_size_of_first_chars.keys():
                                self._font_size_of_first_chars[char.size] = 0
                            self._font_size_of_first_chars[char.size] += 1
                            if char.fontname not in self._font_of_first_chars.keys():
                                self._font_of_first_chars[char.fontname] = 0
                            self._font_of_first_chars[char.fontname] += 1
                            nb_chars += 1
                nb_chars = nb_limit_chars
                first_line = False
        self._font_size_of_first_chars = round(max(self._font_size_of_first_chars,
                                                   key=self._font_size_of_first_chars.get))
        self._font_of_first_chars = max(self._font_of_first_chars, key=self._font_of_first_chars.get)

        self._major_font = max(self._fonts, key=self._fonts.get)
        self._major_font_size = round(max(self._font_sizes, key=self._font_sizes.get))

        char_height = self.major_font_size
        self._line_spacing = (self.height - lines_count *
                              char_height) / lines_count

    @property
    def major_font(self):
        return self._major_font

    @property
    def major_font_size(self):
        return self._major_font_size

    @property
    def font_size_of_first_words(self):
        return self._font_size_of_first_chars

    @property
    def font_of_first_words(self):
        return self._font_of_first_chars

    def __len__(self):
        return len(self._string)

    def __contains__(self, word):
        return word in self._string

    def __repr__(self):
        return f"<F={repr(self.major_font)} FS={repr(self.major_font_size)}> {self._position} [{self.width}, {self.height}]\n{repr(self._string)}"

    def __str__(self):
        if self._is_title:
            title_info = " TITLE"
        else:
            title_info = ""

        return f"-----------{title_info}\n{self._string}-----------"

    def hdistance(self, other_content):
        return self._container.hdistance(other_content.container)

    def vdistance(self, other_content):
        return self._container.vdistance(other_content.container)

    def is_hoverlap(self, other_content):
        return self._container.is_hoverlap(other_content.container)

    def is_voverlap(self, other_content):
        return self._container.is_voverlap(other_content.container)

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
    def is_title(self):
        return self._is_title

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
        return starts_with_uppercase(self._string)

    def starts_with_number(self):
        return starts_with_number(self._string)

    def matches_footer_pattern(self):
        return TextContentResult.footer_regex.match(self._string) is not None

    def is_in_major_size(self, doc_major_size):
        return self.major_font_size == doc_major_size

    def is_less_than_major_size(self, doc_major_size):
        return self.major_font_size < doc_major_size

    def has_short_height(self, doc_major_size):
        return self.height < 2 * doc_major_size

    def is_short(self, max_len):
        return len(self) <= max_len

    def must_split(self):
        lines = self._string.splitlines()
        if len(lines) <= 1:
            return False

        l1 = lines[0]

        #print(repr(self))
        #print("1st F: ", self._first_font)
        #print("1st FS: ", self._first_font_size)
        #print("major F: ", self.major_font)
        #print("major FS: ", self.major_font_size)
        #print("TITLE ?")
        #string_is_title(l1, debug=True)

        #print("must split = ", string_is_title(l1) and (self._first_font != self._major_font or self._first_font_size != self._major_font_size))

        # La première est un titre ET a une police ou taille différente du reste du content
        return string_is_title(l1) and (self._first_font != self._major_font or self._first_font_size != self._major_font_size)


    def split(self):
        lines = self._string.splitlines(True)
        l1 = lines.pop(0)

        c1 = copy.deepcopy(self) # première ligne
        c2 = copy.deepcopy(self) # lignes suivantes

        c1.position = (
            c1.position[0],
            c1.position[3] + self._major_font_size, # on remonte le bord inférieur de la première ligne
            c1.position[2],
            c1.position[3]
        )

        c2.position = (
            c2.position[0],
            c2.position[1],
            c2.position[2],
            c2.position[3] - self._major_font_size # on descend le bord supérieur du content des lignes suivantes
        )

        c1._string = l1
        c1._is_title = True

        c2._string = "".join(lines)

        return c1, c2


    def is_near_vertical(self, other, page_height):
        #print("*********** IS NEAR VERT ***************")
        #print(repr(self))
        #print("-----------------")
        #print(repr(other))
        #print("-----------------")
        #print(f"c1.MF '{self._major_font}'  =  c2.MF '{other._major_font}' ?    {self._major_font == other.major_font}")
        #print(f"c1.MFS '{self._major_font_size}'  =  c2.MFS '{other._major_font_size}' ?    {self._major_font_size == other.major_font_size}")
        
        # Si dans le quart du haut => ne fusionne pas
        #upper_half = 0.5 * page_height
        #in_upper_half = self._position[3] >= upper_half or other.position[3] >= upper_half

        return not (string_is_title(self._string) or string_is_title(other.string)) and\
            approx_equal(self.hdistance(other), 0, 2) and\
            not (self._is_title or other._is_title) and\
            self._major_font == other.major_font and\
            self._major_font_size == other.major_font_size and\
            self.vdistance(other) <= self._major_font_size #and\
            #not in_upper_half

    def vertical_merge(self, other, splitted_word=False):
        self._string += other.string
        self._position = (
            other.position[0], other.position[1],
            self._position[2], self._position[3]
        )


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    UNDEFINED = 2
