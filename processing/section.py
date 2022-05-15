from enum import Enum, unique


class Section(Enum):
    TITLE = 0
    AUTHOR = 1
    ABSTRACT = 2
    KEYWORDS = 3
    INTRODUCTION = 4
    BODY = 5
    DISCUSSION = 6
    CONCLUSION = 7
    REFERENCES = 8
    FINAL = 9
    ANONYMOUS = 10

    def next(self):
        if self == Section.BODY:
            return self
        elif Section.TITLE <= self < Section.FINAL:
            return Section(self.value + 1)
        else:
            return None

    def __ne__(self, other):
        if self.__class__ is other.__class__:
            return self.value != other.value
        return NotImplemented

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class SafeAnalyzer:

    def __init__(self, before_process, after_process, ignore_abstract):
        # Attributes
        self.contents = before_process.contents
        self.result = after_process
        self._title_font = None
        self._title_size = None
        self._buffer = ""
        # Init process
        self._search_section_format()
        self._ignore_abstract = ignore_abstract

    def _search_section_format(self):
        for content in self.contents:
            for label in ["introduction", "discussion", "conclusion", "references"]:
                if label in content.string.strip().lower()[:20]:
                    self._title_font = content.major_font
                    self._title_size = content.major_font_size
                    break
            if self._title_size is not None:
                break

    def processing(self, search=Section.ABSTRACT):
        if self._title_size is None:
            return
        section = None
        for content in self.contents:
            #print("------------------------------")
            #print(content.string)
            new_section = self._match_section(content, search)
            if new_section is None:
                self._buffer += content.string
                #print("====== ADDED TO BUFFER")
            else:
                if new_section != section:
                    self._flush_buffer(section)
                    #print("====== FLUSH BUFFER")
                    # Nouvelle section reconnue
                    if new_section != Section.ANONYMOUS:
                        search = new_section.next()
                        section = new_section
                    # Nouvelle section anonyme
                    else:
                        section = None
                        # Fin de traitement
                        if search == Section.FINAL:
                            break
                    #print("====== SECTION ", section)
                if new_section == Section.ABSTRACT and len(content.string) > 20 or new_section == Section.BODY:
                    self._buffer += content.string
                    #print("====== ADDED TO BUFFER (SPECIAL)")
        self._flush_buffer(section)

    def _match_section(self, content, section):
        string = content.string.strip().lower()
        # Sections avec format personnalisé
        if section <= Section.ABSTRACT:
            if "abstract" in string[:15] or "this article" in string[:75]:
                return Section.ABSTRACT
            else:
                return None
        if section <= Section.KEYWORDS:
            if "keywords" in string[:15] or "index terms" in string[:15]:
                return Section.KEYWORDS
        if section <= Section.REFERENCES:
            if "references" in string[:15]:
                return Section.REFERENCES
        # Sections avec format classique
        if content.major_font == self._title_font and content.major_font_size == self._title_size:
            if section <= Section.INTRODUCTION:
                if "introduction" in string[:20]:
                    return Section.INTRODUCTION
            if section <= Section.BODY:
                if self._match_section(content, Section.DISCUSSION) == Section.ANONYMOUS:
                    return Section.BODY
            if section <= Section.DISCUSSION:
                if "discussion" in string[:20]:
                    return Section.DISCUSSION
            if section <= Section.CONCLUSION:
                if "conclusion" in string[:20]:
                    return Section.CONCLUSION
            return Section.ANONYMOUS
        return None

    def _flush_buffer(self, section):
        if section == Section.ABSTRACT and not self._ignore_abstract:
            self.result.abstract = self._buffer
        elif section == Section.INTRODUCTION:
            self.result.introduction = self._buffer
        elif section == Section.BODY:
            self.result.body = self._buffer
        elif section == Section.DISCUSSION:
            self.result.discussion = self._buffer
        elif section == Section.CONCLUSION:
            self.result.conclusion = self._buffer
        elif section == Section.REFERENCES:
            self.result.references = self._buffer
        self._buffer = ""


def section_extraction(result, text_processing_result, ignore_abstract = False):
    analyzer = SafeAnalyzer(result, text_processing_result, ignore_abstract)
    analyzer.processing()
