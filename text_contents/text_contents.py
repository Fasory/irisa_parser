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

    def merge_all(self):
        self.merge_horizontal()
        self.merge_vertical()

        for c in self._contents:
            c.reconstitute_words()

    def merge_horizontal(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            merged = self._contents[i]
            first_pos = merged.position
            last_pos = first_pos
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_horizontal(self._contents[j + 1]):
                #print("------MERGE H----")
                # print(merged.string,
                #      "*******\n", self._contents[j + 1].string)
                # print("================")

                next = self._contents[j + 1]
                merged.merge_horizontal(next)
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

    def merge_vertical(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            merged = self._contents[i]
            first_pos = merged.position
            last_pos = first_pos
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_vertical(self._contents[j + 1]):
                #print("------MERGE V----")
                # print(merged.string,
                #      "*******\n", self._contents[j + 1].string)
                # print("================")

                next = self._contents[j + 1]
                merged.merge_vertical(next)
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

        #print(self._string, self._position)

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
                                self._first_font_size = line.size
                                self._first_font = line.fontname
                            elif self._first_font_size != line.size or self._first_font != line.fontname:
                                self._first_font_size = None
                                self._first_font = None
                                first_line = False
                first_line = False
        char_height = self.major_font_size()
        self._line_spacing = (self.height - lines_count *
                              char_height) / (lines_count)

    def __str__(self):
        return f"{self._position}\n'{self._string}'"

    def __repr__(self):
        return f"<{self._string}>"

    def hdistance(self, other_content):
        return self._container.hdistance(other_content.container)

    def vdistance(self, other_content):
        return self._container.vdistance(other_content.container)

    @property
    def container(self):
        return self._container

    @property
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

    def major_font(self):
        return max(self._fonts, key=self._fonts.get)

    def major_font_size(self):
        return max(self._font_sizes, key=self._font_sizes.get)

    def starts_with_title(self):
        first_line = self._string.splitlines()[0]
        return first_line[0].isnumeric() and ("introduction") in first_line[1:].lower()

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

    @staticmethod
    def _check_word(word):
        return EnglishVocab.instance().check_word(word)

    def is_near_horizontal(self, other):
        hd = self.hdistance(other)

        self_h = self._container.height
        other_h = other._container.height

        self_font_size = self.major_font_size()
        other_font_size = other.major_font_size()
        # print(
        #    f"is_near: selfH={self_h}, otherH={other_h}, fontS={self_font_size}, otherFS={other_font_size}, dh={hd}")

        # Si c'est sur une seule ligne
        if self_h == other_h and self_h == self_font_size and self_font_size == other_font_size:
            # Si dh < char_margin
            if hd < 10:  # char_margin
                return True

        return False

    def is_near_vertical(self, other):
        hd = self.hdistance(other)

        vd = self.vdistance(other)

        self_font_size = self.major_font_size()
        other_font_size = other.major_font_size()

        self_font = self.major_font()
        other_font = other.major_font()
        #print(f"---\n{self._string}\n{other.string}\nfontS={self_font_size}, otherFS={other_font_size}, selfF={self_font}, otherF={other_font}, dv={vd}, spacing={self._line_spacing}, dh={hd}")

        # Doivent être l'un par-dessus l'autre
        if hd > 1:
            return False

        # Si titre après => non
        if other.starts_with_title():
            return False

        words = self._string.split(" ")
        last = words[-1]
        if last.endswith("-") or last.endswith("- ") or last.endswith("-\n"):
            reconstituted = words[-1][:-1] + other.string.split(" ")[0]
            if TextContentResult._check_word(reconstituted):
                return True

        # Même police
        if self_font_size == other_font_size and self_font.lower() == other_font.lower():
            # Espace inférieur à l'interligne, OU à la taille d'un caractère
            if vd < self.major_font_size() or vd < self._line_spacing:
                return True

        return False

    def merge_horizontal(self, other):
        self._string = self._string.replace("\n", "")
        other._string = other.string.replace("\n", "")
        #print(f"merge fn: '{self._string}' + '{other.string}'")

        self._string += other.string
        self._position = (
            self._position[0],
            self._position[1],
            other.position[2],
            other.position[3]
        )

    def merge_vertical(self, other):
        words = self._string.split(" ")
        other_words = other.string.split(" ")
        if words[-1].endswith("-\n") or words[-1].endswith("- ") or words[-1].endswith("-"):
            reconstituted = words[-1][:-1] + other_words[0]
            #print("RECONSTI", reconstituted)
            if TextContentResult._check_word(reconstituted):
                words[-1] = reconstituted
                other_words.pop(0)
                self._string = " ".join(words)
                other._string = " ".join(other_words)

        self._string += "\n" + other.string

    def reconstitute_words(self):
        self._string = self.string.replace("- ", "-")\
            .replace("-\n", "-").replace(":", " :")\
            .replace(".", " .").replace(",", " ,")\
            .replace(";", " ;").replace("!", " !")\
            .replace("?", " ?")

        words = self.string.split(" ")

        for i in range(len(words)):
            w = words[i]
            if "-" in w:
                new = w.replace("-", "").replace("\n", "")
                #print("RECONSTI for", new, end="")
                if TextContentResult._check_word(new):
                    words[i] = new
                    #print("    ok")
                # print("")

        self._string = " ".join(words).replace(" :", ":")\
            .replace(" .", ".").replace(" ,", ",")\
            .replace(" ;", ";").replace(" !", "!")\
            .replace(" ?", "?")


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    UNDEFINED = 2
