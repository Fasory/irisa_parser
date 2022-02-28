
class FinalStat:
    """
    Cette classe va nous servir à stocker le dossier d'arrivée
    """

    def __init__(self):
        """ Constructor """
        self._options = {"t": False, "x": False}

    def addOption(self, option):
        if(option == "x"):
          self._options["x"] = True
        if(option == "t"):
          self._options["t"] = True

    @property
    def _optionsList(self):
        for option in self._options.values() :
            if(option == True) :
                return self._options
        self._options["t"] = True
        return self._options