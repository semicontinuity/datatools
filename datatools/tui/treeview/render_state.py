class RenderState:
    is_under_cursor: bool

    def __init__(self, is_under_cursor) -> None:
        self.is_under_cursor = is_under_cursor
