from datatools.tui.buffer.blocks.block import Block


class AutoBlock(Block):
    contents: object

    def __init__(self):
        self.width = 1
        self.height = 1
