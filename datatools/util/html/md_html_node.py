class MdHtmlNode:

    def __init__(self, *contents) -> None:
        self.contents = contents

    def __str__(self):
        s = '\n'.join(str(e) for e in self.contents)
        return f"""
::: html

{s}

:::
"""
