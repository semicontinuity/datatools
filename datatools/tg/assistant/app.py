#!/usr/bin/env python3
import asyncio
import os
import sys
from typing import Tuple, Any

from picotui.defs import KEY_ENTER

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jv.highlighting.console import ConsoleHighlighting
from datatools.jv.highlighting.holder import set_current_highlighting, get_current_highlighting
from datatools.tg import cache_folder, new_telegram_client
from datatools.tg.assistant.view.document import TgDocument
from datatools.tg.assistant.view.document_factory import TgDocumentFactory
from datatools.tg.assistant.view.grid import TgGrid
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.util.object_exporter import init_object_exporter, ObjectExporter


def make_tg_tree_applet(document: TgDocument, screen_size, popup: bool = False):
    screen_width, screen_height = screen_size
    grid_context = GridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_tg_tree_applet(grid_context, popup, document)


def do_make_tg_tree_applet(grid_context: GridContext, popup, document: TreeDocument):
    return Applet(
        'jv',
        grid(document, grid_context, grid_class=TgGrid),
        DataBundle(None, None, None, None, None),
        popup
    )


def loop(document: TgDocument):
    return do_loop(make_grid(document))


def make_grid(document: TgDocument):
    return make_tg_tree_applet(document, screen_size_or_default()).g


def do_loop(g):
    loop_result = g.loop()
    cur_line = g.cur_line
    return loop_result, cur_line


def handle_loop_result(document, key_code, cur_line: int) -> Tuple[int, Any]:
    if key_code == KEY_ENTER:
        return EXIT_CODE_ENTER, ''


if ObjectExporter.INSTANCE is None:
    init_object_exporter()
if get_current_highlighting() is None:
    set_current_highlighting(ConsoleHighlighting())


async def do_main(folder, client):
    doc: TgDocument = await TgDocumentFactory(folder, client).make_document()
    key_code, cur_line = with_alternate_screen(lambda: loop(doc))
    exit_code, output = handle_loop_result(doc, key_code, cur_line)
    if output is not None:
        print(output)
    sys.exit(exit_code)


async def main():
    telethon_session_slug = os.environ['TELETHON_SESSION_SLUG']
    folder = cache_folder(telethon_session_slug)

    async with await new_telegram_client(telethon_session_slug) as client:
        await do_main(folder, client)


if __name__ == "__main__":
    asyncio.run(main())
