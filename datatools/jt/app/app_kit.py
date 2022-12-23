import json
import signal
import sys
from dataclasses import dataclass
from json import JSONDecodeError
from typing import List

from picotui.screen import Screen

from datatools.json.util import dataclass_from_dict, to_jsonisable
from datatools.jt.logic.auto_metadata import enrich_metadata
from datatools.jt.logic.auto_presentation import enrich_presentation
from datatools.jt.model.data_bundle import DataBundle, STATE_TOP_LINE, STATE_CUR_LINE, STATE_CUR_LINE_Y
from datatools.jt.model.exit_codes import EXIT_CODE_ESCAPE
from datatools.jt.model.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jt.ui.classic.grid import WGrid
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererColoredPlain, ColumnRendererColoredHash, \
    ColumnRendererColoredMapping
from datatools.jt.ui.ng.cell_renderer_dict_index import ColumnRendererDictIndexHashColored
from datatools.jt.ui.ng.cell_renderer_indicator import ColumnRendererIndicator
from datatools.jt.ui.ng.cell_renderer_seq_diagram_call import ColumnRendererSeqDiagramCall
from datatools.jt.ui.ng.cell_renderer_seq_diagram_call2 import ColumnRendererSeqDiagramCall2
from datatools.jt.ui.ng.cell_renderer_stripes_hashes import ColumnRendererStripesHashColored
from datatools.jt.ui.ng.cell_renderer_stripes_time_series import ColumnRendererStripesTimeSeries
from datatools.tui.picotui_patch import get_screen_size, patch_picotui
from datatools.tui.picotui_util import with_raw_term, screen_unprepare, screen_prepare
from datatools.tui.terminal import with_raw_terminal, read_screen_size
from datatools.tui.tui_fd import infer_fd_tui
from datatools.util.meta_io import metadata_or_default, presentation_or_default, state_or_default, write_state_or_pass
from datatools.util.meta_io import write_presentation_or_pass, write_metadata_or_pass


@dataclass
class Params:
    title: str = None
    stream_mode: bool = None
    watch_mode: bool = None
    compact: bool = None
    print: bool = None
    pretty_print: bool = None


# NB: we do not need to keep data_bundle; better to return state from run()
class Applet:
    g: WGrid
    data_bundle: DataBundle
    popup: bool

    def __init__(self, app_id, g, data_bundle: DataBundle, popup: bool = False):
        self.app_id = app_id
        self.g = g
        self.data_bundle = data_bundle
        self.popup = popup
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)

    def handle_sigwinch(self, signalNumber, frame):
        screen_size = Screen.screen_size()  # not very stable, sometimes duplicate 'x1b[8' is read
        self.g.width = screen_size[0]
        self.g.height = screen_size[1]
        self.g.redraw()

    def redraw(self):
        self.g.redraw()

    def run(self):
        res = self.g.loop()
        exit_code = KEYS_TO_EXIT_CODES.get(res)
        self.data_bundle.state = {
            STATE_TOP_LINE: self.g.top_line,
            STATE_CUR_LINE: self.g.cur_line,
            STATE_CUR_LINE_Y: self.g.line_y(self.g.cur_line)
        }
        return exit_code if exit_code is not None else EXIT_CODE_ESCAPE


def do_main(app_id, app_f, g, router, screen_size):
    params = parse_params(sys.argv)

    def loop():
        exit_code = None
        data_bundle = None

        for orig_data in load_data(params):
            if len(orig_data) == 0:
                sys.exit(255)
            data_bundle = load_data_bundle(params, orig_data)

            if params.print or params.pretty_print:
                if params.pretty_print: print()
                exit_code = paint(g, data_bundle, with_raw_terminal(read_screen_size))
                if params.pretty_print: print()
                break
            else:
                exit_code = with_raw_term(alt_screen=True, f=lambda: app_loop(app_f, app_id, data_bundle, g, router, screen_size))

        return exit_code, data_bundle

    exit_code, data_bundle = loop()
    store_data_bundle(data_bundle)
    return exit_code


def main(applet_id, applet_f, g, router):
    fd_tui = infer_fd_tui()
    screen_size = with_raw_terminal(get_screen_size)  # works only before patch(?) in 'long pipe'
    patch_picotui(fd_tui, fd_tui)
    sys.exit(do_main(applet_id, applet_f, g, router, screen_size))


def app_loop(applet_f, applet_id, data_bundle, g, router, screen_size) -> int:
    the_grid = g(screen_size, data_bundle)
    a = applet_f(applet_id, the_grid, data_bundle)
    applet_stack = [a]
    prev_applet = None
    exit_code = 0

    while True:
        if prev_applet is not None:
            screen_unprepare(True, not prev_applet.popup)

        if not applet_stack:
            break
        the_applet = applet_stack.pop()

        screen_prepare(True, not the_applet.popup)
        try:
            exit_code = the_applet.run()
        except Exception as ex:
            screen_unprepare(True, not the_applet.popup)
            raise ex

        new_applet = router(the_applet, exit_code)

        prev_applet = the_applet
        if new_applet is None:  # means this applet does not launch sub-applet, i.e. terminates
            continue
        elif new_applet != the_applet:
            if new_applet.popup:
                prev_applet = None
            applet_stack.append(the_applet)  # was popped, restore
            applet_stack.append(new_applet)
    return exit_code


def paint(g, data_bundle: DataBundle, screen_size):
    screen_size = screen_size[0], len(data_bundle.orig_data) + 1
    the_grid = g(screen_size, data_bundle)
    the_grid.cur_line = -1
    the_grid.interactive = False
    the_grid.redraw()


def load_data_bundle(params: Params, orig_data: List):
    raw_metadata = metadata_or_default(default={})
    raw_presentation = presentation_or_default(default={})
    state = state_or_default(default=default_state())

    if len(raw_metadata) == 0 and len(raw_presentation) == 0 and params.compact:
        orig_data = [{'_': orig_data}]
    metadata = dataclass_from_dict(Metadata, raw_metadata, {'Metadata': Metadata})
    presentation = dataclass_from_dict(
        Presentation,
        raw_presentation,
        {
            'Presentation': Presentation,
            ColumnRendererColoredPlain.type: ColumnRendererColoredPlain,
            ColumnRendererColoredHash.type: ColumnRendererColoredHash,
            ColumnRendererColoredMapping.type: ColumnRendererColoredMapping,
            ColumnRendererDictIndexHashColored.type: ColumnRendererDictIndexHashColored,
            ColumnRendererIndicator.type: ColumnRendererIndicator,
            ColumnRendererSeqDiagramCall.type: ColumnRendererSeqDiagramCall,
            ColumnRendererSeqDiagramCall2.type: ColumnRendererSeqDiagramCall2,
            ColumnRendererStripesTimeSeries.type: ColumnRendererStripesTimeSeries,
            ColumnRendererStripesHashColored.type: ColumnRendererStripesHashColored
        }
    )
    if params.title is not None:
        presentation.title = params.title

    metadata = enrich_metadata(orig_data, metadata)
    presentation = enrich_presentation(orig_data, metadata, presentation)
    return DataBundle(orig_data, metadata, presentation, state)


def store_data_bundle(data_bundle: DataBundle):
    write_state_or_pass(data_bundle.state)
    write_presentation_or_pass(to_jsonisable(data_bundle.presentation))
    write_metadata_or_pass(to_jsonisable(data_bundle.metadata))


def default_state():
    return {'top_line': 0, 'cur_line': 0}


def load_data(params: Params):
    if params.stream_mode:
        orig_data = []
        i = 0
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            try:
                j = json.loads(line)
            except JSONDecodeError:
                print(f"Cannot decode JSON line {i}: {line}", file=sys.stderr)
                sys.exit(255)
            orig_data.append(j)
            i += 1
        yield orig_data
    elif params.watch_mode:
        i = 0
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            try:
                yield json.loads(line)
            except JSONDecodeError:
                print(f"Cannot decode JSON line {i}: {line}", file=sys.stderr)
                sys.exit(255)
            i += 1
    else:
        data = sys.stdin.read()
        try:
            yield json.loads(data)
        except JSONDecodeError as e:
            print("Cannot decode JSON", file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(255)


def parse_params(argv) -> Params:
    params = Params()
    a = 1
    while a < len(argv):
        if sys.argv[a] == '-t':
            a += 1
            params.title = sys.argv[a]
        elif sys.argv[a] == "-s":
            params.stream_mode = True
        elif sys.argv[a] == "-w":
            params.watch_mode = True
        elif sys.argv[a] == '-c':
            params.compact = True
        elif sys.argv[a] == '-p':
            params.print = True
        elif sys.argv[a] == '-P':
            params.pretty_print = True
        a += 1
    return params
