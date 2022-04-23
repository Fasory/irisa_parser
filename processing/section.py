from enum import unique, Enum


@unique
class Section(Enum):
    TITLE = 0
    AUTHOR = 1
    ABSTRACT = 2
    INTRODUCTION = 3
    BODY = 4
    DISCUSSION = 5
    CONCLUSION = 6
    REFERENCE = 7
    ANONYMOUS = 8

    def __int__(self):
        if self == self.ANONYMOUS:
            self._next = []
        elif self == self.BODY:
            self._next = [self.TITLE,
                          self.AUTHOR,
                          self.ABSTRACT,
                          self.INTRODUCTION,
                          self.BODY,
                          self.DISCUSSION,
                          self.CONCLUSION,
                          self.REFERENCE][self.value:]
        else:
            self._next = [self.TITLE,
                          self.AUTHOR,
                          self.ABSTRACT,
                          self.INTRODUCTION,
                          self.BODY,
                          self.DISCUSSION,
                          self.CONCLUSION,
                          self.REFERENCE][self.value + 1:]

    def create_ananymous(self):
        section = self.ANONYMOUS
        section._next = self._next
        return section

    def match_string(self, content, major_font, major_font_size):
        if self == self.TITLE:
            return content.major_font_size > major_font_size
        elif self == self.AUTHOR:
            return True
        elif self == self.ABSTRACT:
            return content.major_font == major_font and content.major_font_size == major_font_size or \
                content.major_font_size >= major_font_size*0.75 and content.major_font != major_font
        elif self == self.INTRODUCTION:
            return content.major_font == major_font and content.major_font_size == major_font_size
        elif self == self.BODY:
            return content.major_font == major_font and content.major_font_size == major_font_size
        elif self == self.DISCUSSION:
            return content.major_font == major_font and content.major_font_size == major_font_size
        elif self == self.CONCLUSION:
            return content.major_font == major_font and content.major_font_size == major_font_size
        elif self == self.REFERENCE:
            return content.major_font == major_font and content.major_font_size == major_font_size or \
                content.major_font_size >= major_font_size*0.75 and content.major_font != major_font
        return False

    def flush_buffer(self, buffer, text_processing_result):
        if self == self.TITLE:
            text_processing_result.title = buffer
        elif self == self.AUTHOR:
            text_processing_result.authors = buffer
        elif self == self.ABSTRACT:
            text_processing_result.abstract = buffer
        elif self == self.INTRODUCTION:
            text_processing_result.introduction = buffer
        elif self == self.BODY:
            text_processing_result.body = buffer
        elif self == self.DISCUSSION:
            text_processing_result.discussion = buffer
        elif self == self.CONCLUSION:
            text_processing_result.conclusion = buffer
        elif self == self.REFERENCE:
            text_processing_result.references = buffer

    def find_next_section_with(self, content, major_font, major_font_size):
        for section in self._next:
            if section.match_next(content, major_font, major_font_size):
                if section == self.ANONYMOUS:
                    return self.create_ananymous()
                else:
                    return section
        return None

    def math_next(self, content, major_font, major_font_size):
        target = content.string.strip().lower()
        if self == self.TITLE:
            pass
        elif self == self.AUTHOR:
            pass
        elif self == self.ABSTRACT:
            return "abstract" in target[:15] or "this article" in target[:25] or "we present" in target[:40]
        elif self == self.INTRODUCTION:
            return "introduction" in target[:20] and \
                   (content.major_font_size > major_font_size
                    or content.major_font != major_font and content.major_font_size == major_font_size)
        elif self == self.BODY:
            for other_section in self.BODY._next[1:]:
                if other_section != self.ANONYMOUS and other_section.math_next(content, major_font, major_font_size):
                    return False
            return content.major_font_size > major_font_size or content.major_font != major_font and \
                content.major_font_size == major_font_size
        elif self == self.DISCUSSION:
            return "discussion" in target[:20] and \
                   (content.major_font_size > major_font_size
                    or content.major_font != major_font and content.major_font_size == major_font_size)
        elif self == self.CONCLUSION:
            return "conclusion" in target[:20] and \
                   (content.major_font_size > major_font_size
                    or content.major_font != major_font and content.major_font_size == major_font_size)
        elif self == self.REFERENCE:
            return "references" in target[:20] and \
                   (content.major_font_size > major_font_size
                    or content.major_font != major_font and content.major_font_size == major_font_size)
        elif self == self.ANONYMOUS:
            return content.major_font_size > major_font_size \
                   or content.major_font != major_font and content.major_font_size == major_font_size
        return False


def section_extraction(result, text_processing_result, first_research, limit_research=None):
    current_section = first_research
    buffer_section = ""
    for content in result.contents:
        if current_section is not None and current_section.match_string(content,
                                                                        result.major_font,
                                                                        result.major_font_size):
            buffer_section += content.string
        else:
            if current_section is None:
                break
            next_section = current_section.find_next_section_with(content, result.major_font, result.major_font_size)
            if next_section is not None:
                current_section.flush_buffer(buffer_section, text_processing_result)
                buffer_section = ""
                if limit_research == next_section:
                    break
                current_section = next_section
