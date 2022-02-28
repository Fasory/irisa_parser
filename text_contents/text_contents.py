from enum import Enum, unique
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal, LTTextLineVertical, LTChar, LTTextLine

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
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_horizontal(self._contents[j + 1]):
                #print("------MERGE H----")
                # print(merged.string,
                #      "*******\n", self._contents[j + 1].string)
                # print("================")

                next = self._contents[j + 1]
                merged.merge_horizontal(next)

                j += 1

            new_contents.append(merged)
            # print(new_contents)
            i = j + 1

        self._contents = new_contents

    def merge_vertical(self):
        new_contents = []

        i = 0
        while i < len(self._contents):
            merged = self._contents[i]
            j = i

            while j + 1 < len(self._contents) and self._contents[j].is_near_vertical(self._contents[j + 1]):
                #print("------MERGE V----")
                # print(merged.string,
                #      "*******\n", self._contents[j + 1].string)
                # print("================")

                next = self._contents[j + 1]
                merged.merge_vertical(next)

                j += 1

            new_contents.append(merged)
            # print(new_contents)
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

        for line in elt:
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

    def __str__(self):
        return self._string

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
    def string(self):
        """ Get raw string of content """
        return self._string

    @property
    def position(self):
        """ Get position of content """
        return self._position

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

    def process_accents(self):
        self._string = self._string.replace("´A", "Á").replace("¨A", "Ä").replace("`A", "À").replace("^A", "Â")\
            .replace("´a", "á").replace("¨a", "ä").replace("`a", "à").replace("^a", "â").replace("´E", "É")\
            .replace("¨E", "Ë").replace("`E", "È").replace("^E", "Ê").replace("´e", "é").replace("¨e", "ë")\
            .replace("`e", "è").replace("^e", "ê").replace("c¸", "ç").replace("´I", "Í").replace("¨I", "Ï")\
            .replace("`I", "Ì").replace("^I", "Î").replace("´i", "í").replace("¨i", "ï").replace("`i", "ì")\
            .replace("^i", "î").replace("´O", "Ó").replace("¨O", "Ö").replace("`O", "Ò").replace("^O", "Ô")\
            .replace("´o", "ó").replace("¨o", "ö").replace("`o", "ò").replace("^o", "ô").replace("´U", "Ú")\
            .replace("¨U", "Ü").replace("`U", "Ù").replace("^U", "Û").replace("´u", "ú").replace("¨u", "ü")\
            .replace("`u", "ù").replace("^u", "û").replace("´Y", "Ý").replace("¨Y", "Ÿ").replace("`Y", "Ỳ")\
            .replace("^Y", "Ŷ").replace("´y", "ý").replace("¨y", "ÿ").replace("`y", "ỳ").replace("^y", "ŷ")

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
            if hd < 100:  # char_margin
                return True

        return False

    def is_near_vertical(self, other):
        vd = self.vdistance(other)

        self_font_size = self.major_font_size()
        other_font_size = other.major_font_size()

        self_font = self.major_font()
        other_font = other.major_font()
        # print(
        #    f"is_nearV: fontS={self_font_size}, otherFS={other_font_size}, dv={vd}")

        words = self._string.split(" ")
        if words[-1].endswith("-"):
            reconstituted = words[-1][:-1] + other.string.split(" ")[0]
            if TextContentResult._check_word(reconstituted):
                return True

        if vd < 60 and self_font_size == other_font_size and self_font.lower() == other_font.lower():
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
            print("RECONSTI", reconstituted)
            if TextContentResult._check_word(reconstituted):
                words[-1] = reconstituted
                other_words.pop(0)
                self._string = " ".join(words)
                other._string = " ".join(other_words)

        self._string += other.string

        self._position = (
            self._position[0],
            self._position[1],
            other.position[2],
            other.position[3]
        )

    def reconstitute_words(self):
        self._string = self.string.replace("- ", "-")
        words = self.string.split(" ")

        for i in range(len(words)):
            w = words[i]
            if "-" in w:
                new = w.replace("-", "")
                new = new.replace("\n", "")
                print("RECONSTI for", new, end="")
                if TextContentResult._check_word(new):
                    words[i] = new
                    print("    ok")
                print("")

        self._string = " ".join(words)


@unique
class TextAlignment(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    UNDEFINED = 2
