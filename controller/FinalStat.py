
class FinalStat:
    """
    Cette classe va nous servir à stocker le dossier d'arrivée
    """

    def __init__(self):
        """ Constructor """
        self._options = {"text": False, "xml": False}

    def addOption(self, option, value):
        self._options[option] = value

    @property
    def _optionsList(self):
        for option in self._options.values() :
            if(option == True) :
                return self._options
        self._options["text"] = True
        return self._options