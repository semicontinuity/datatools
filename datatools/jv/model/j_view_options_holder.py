import os

from datatools.jv.model import JViewOptions


class JViewOptionsHolder:
    options: JViewOptions

    def __init__(self, options: JViewOptions = None) -> None:
        if options is None:
            json = 'YAML' not in os.environ
            options = JViewOptions(
                quotes=json,
                commas=json,
            )
        self.options = options
