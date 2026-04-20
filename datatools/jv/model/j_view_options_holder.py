import os

from datatools.jv.model import JViewOptions


class JViewOptionsHolder:
    options: JViewOptions

    def __init__(self, options: JViewOptions = None) -> None:
        if options is None:
            options = JViewOptionsHolder.infer_options()
        self.options = options

    @staticmethod
    def infer_options():
        json = 'YAML' not in os.environ
        return JViewOptions(
            quotes=json,
            commas=json,
        )
