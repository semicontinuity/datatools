from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, AnyStr, List

from datatools.tui.ansi_str import ANSI_CMD_DEFAULT_FG, ANSI_CMD_ATTR_NOT_BOLD, ANSI_CMD_ATTR_BOLD
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.terminal import ansi_foreground_escape_code


@dataclass
class Style:
    attr: int = 0
    fg: Optional[Sequence[int]] = None


def render(spans: List[Tuple[AnyStr, Style]]) -> list[AnyStr]:
    return [render_style(span[1]) + span[0] + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD for span in spans]


def render_substr(spans: List[Tuple[AnyStr, Style]], start, end) -> list[AnyStr]:
    result = ''
    span_start = 0

    for span in spans:
        span_end = span_start + len(span[0])
        if span_end <= start:
            continue

        remains = end - span_start
        if remains <= 0:
            break

        s = span[0][:remains]
        result += render_style(span[1]) + s + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD

        span_start += len(s)

    return result + ' ' * (end - span_start)


def render_style(style: Style) -> AnyStr:
    result = ''
    if style.fg is not None:
        result += ansi_foreground_escape_code(*style.fg)
    if style.attr & AbstractBufferWriter.MASK_BOLD != 0:
        result += ANSI_CMD_ATTR_BOLD
    return result
