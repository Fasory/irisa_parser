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

    def next(self):
        return [self.TITLE,
                self.AUTHOR,
                self.ABSTRACT,
                self.INTRODUCTION,
                self.BODY,
                self.DISCUSSION,
                self.CONCLUSION,
                self.REFERENCE][self:]

    def get_form(self):
        return None
