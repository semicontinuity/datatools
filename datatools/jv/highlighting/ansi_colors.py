from datatools.jv.highlighting.rich_text import Style
from datatools.tui.ansi_str import ansi_cmd_set_fg, ANSI_CMD_ATTR_NOT_BOLD, ANSI_CMD_DEFAULT_FG
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter

C_BLACK = 0
C_RED = 1
C_GREEN = 2
C_YELLOW = 3
C_BLUE = 4
C_MAGENTA = 5
C_CYAN = 6
C_WHITE = 7
ATTR_INTENSITY = 8
C_GRAY = C_BLACK | ATTR_INTENSITY
C_B_RED = C_RED | ATTR_INTENSITY
C_B_GREEN = C_GREEN | ATTR_INTENSITY
C_B_YELLOW = C_YELLOW | ATTR_INTENSITY
C_B_BLUE = C_BLUE | ATTR_INTENSITY
C_B_MAGENTA = C_MAGENTA | ATTR_INTENSITY
C_B_CYAN = C_CYAN | ATTR_INTENSITY
C_B_WHITE = C_WHITE | ATTR_INTENSITY


class Highlighting:
    CURRENT: 'Highlighting' = None

    def ansi_reset_attrs(self): return ''

    def ansi_set_attrs_field_colon(self): return ''

    def ansi_set_attrs_comma(self): return ''

    def ansi_set_attrs_field_name(self): return ''

    def ansi_set_attrs_null(self): return ''

    def ansi_set_attrs_true(self): return ''

    def ansi_set_attrs_false(self): return ''

    def ansi_set_attrs_number(self): return ''

    def ansi_set_attrs_string(self): return ''

    def for_null(self) -> Style: return Style()

    def for_true(self) -> Style: return Style()

    def for_false(self) -> Style: return Style()

    def for_number(self) -> Style: return Style()

    def for_string(self) -> Style: return Style()

    def for_comma(self) -> Style: return Style()

    def for_colon(self) -> Style: return Style()

    def for_field_name(self) -> Style: return Style()

    def for_curly_braces(self) -> Style: return Style()

    def for_square_brackets(self) -> Style: return Style()


class ConsoleHighlighting(Highlighting):

    def ansi_reset_attrs(self): return ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD

    def ansi_set_attrs_field_colon(self): return ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD

    def ansi_set_attrs_comma(self): return ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD

    def ansi_set_attrs_field_name(self): return ansi_cmd_set_fg(C_YELLOW)

    def ansi_set_attrs_null(self): return ansi_cmd_set_fg(C_B_MAGENTA)

    def ansi_set_attrs_true(self): return ansi_cmd_set_fg(C_B_GREEN)

    def ansi_set_attrs_false(self): return ansi_cmd_set_fg(C_B_BLUE)

    def ansi_set_attrs_number(self): return ansi_cmd_set_fg(C_B_RED)

    def ansi_set_attrs_string(self): return ansi_cmd_set_fg(C_B_CYAN)

    def for_null(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (255, 0, 255))

    def for_true(self): return Style(AbstractBufferWriter.MASK_BOLD, (0, 255, 0))

    def for_false(self): return Style(AbstractBufferWriter.MASK_BOLD, (0, 0, 255))

    def for_number(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (255, 0, 0))

    def for_string(self) -> Style: return Style(AbstractBufferWriter.MASK_BOLD, (0, 255, 255))

    def for_field_name(self): return Style(AbstractBufferWriter.MASK_NONE, (128, 128, 0))
