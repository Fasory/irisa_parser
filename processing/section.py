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

    superTableauDeClement = [["mot1","mot2"],["mot1","mot2"],["mot1","mot2"],["mot1","mot2"],["mot1","mot2"],["mot1","mot2"],["mot1","mot2"]]

    def next(self):
        return [self.TITLE,
                self.AUTHOR,
                self.ABSTRACT,
                self.INTRODUCTION,
                self.BODY,
                self.DISCUSSION,
                self.CONCLUSION,
                self.REFERENCE][self:]

    def laSuperMethodeDeClement(self, content, majortruc):
        if content.major == majortruc:
            return False
        for word in content.string.split(" "):
            if word in self.superTableauDeClement[self.leSuperIdDeClement]:
                return True
        return False

    def get_form(self):
        return None
