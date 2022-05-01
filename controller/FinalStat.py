class FinalStat:
    """
    Cette classe va nous servir à stocker le dossier d'arrivée
    """

    def __init__(self, indir, outdir):
        """ Constructor """
        self._output = outdir
        self._input = indir
        self._options = {}

    def addOption(self, option, value):
        self._options[option] = value

    @property
    def optionsList(self):
        for option in self._options.values():
            if option:
                return self._options
        return self._options

    @property
    def output(self):
        return self._output

    @property
    def input(self):
        return self._input
