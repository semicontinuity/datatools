#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Any

from picotui.defs import KEY_ENTER
from telethon import TelegramClient

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jv.highlighting.console import ConsoleHighlighting
from datatools.jv.highlighting.holder import set_current_highlighting, get_current_highlighting
from datatools.tg import to_cache_folder, new_telegram_client
from datatools.tg.assistant.model.tg_model_factory import TgModelFactory
from datatools.tg.assistant.view.tg_document import TgDocument
from datatools.tg.assistant.view.tg_document_factory import TgDocumentFactory
from datatools.tg.assistant.view.tg_grid import TgGrid
from datatools.tg.assistant.view.tg_view_factory import TgViewFactory
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.tree_document import TreeDocument
from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.tree_grid_factory import tree_grid
from datatools.util.object_exporter import init_object_exporter, ObjectExporter

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')


def make_tg_tree_applet(document: TgDocument, screen_size, popup: bool = False):
    screen_width, screen_height = screen_size
    grid_context = TreeGridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_tg_tree_applet(grid_context, popup, document)


def do_make_tg_tree_applet(grid_context: TreeGridContext, popup, document: TreeDocument):
    return Applet(
        'jv',
        tree_grid(document, grid_context, grid_class=TgGrid),
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


def handle_loop_result(document, key_code, cur_line: int) -> tuple[int, Any]:
    if key_code == KEY_ENTER:
        return EXIT_CODE_ENTER, ''
    else:
        return 0, None


if ObjectExporter.INSTANCE is None:
    init_object_exporter()
if get_current_highlighting() is None:
    set_current_highlighting(ConsoleHighlighting())


def update_footer(doc: TgDocument, model_factory: TgModelFactory):
    while True:
        time.sleep(1)
        summ_qsize = model_factory.message_summarizer_service.work_queue_size()
        weave_qsize = model_factory.topic_messages_weaver.work_queue_size()
        doc.footer = f'Summarize: {summ_qsize} Weave: {weave_qsize}'


async def do_main(folder, client: TelegramClient, since):
    model_factory = TgModelFactory(folder, client, since)
    view_factory = TgViewFactory()
    document_factory = TgDocumentFactory()

    tg_data = await model_factory.make_tg_data()

    doc: TgDocument = document_factory.make_document_for(
        view_factory.make_root(tg_data),
        "footer"
    )

    time_thread = threading.Thread(target=lambda : update_footer(doc, model_factory), daemon=True)
    time_thread.start()

    time.sleep(5)

    key_code, cur_line = with_alternate_screen(lambda: loop(doc))
    exit_code, output = handle_loop_result(doc, key_code, cur_line)
    if output is not None:
        print(output)

    model_factory.close()
    tg_data.save_caches()

    sys.exit(exit_code)


async def main():
    telethon_session_slug = os.environ['TELETHON_SESSION_SLUG']
    folder = to_cache_folder(telethon_session_slug)

    since = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    print(f'Will load discussions since {since}', file=sys.stderr)

    async with await new_telegram_client(telethon_session_slug) as client:
        await do_main(folder, client, since)


if __name__ == "__main__":
    asyncio.run(main())
