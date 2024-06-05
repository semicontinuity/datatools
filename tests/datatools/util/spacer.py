from datatools.tui.buffer.blocks.block import Block


class Spacer(Block):

    def __init__(self, width: int = 0, heigth: int = 0):
        self.width = width
        self.height = heigth
