from datatools.tui.context.buffered_rendering_context import BufferedRenderingContext
from datatools.tui.context.rendering_context import RenderingContext


def demo_001():
    global context
    print('Regular')
    context = BufferedRenderingContext(10, 10)
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!")
    print(str(context) + "\x1b[0m\n")


def demo_002():
    global context
    print('Bold')
    context = BufferedRenderingContext(10, 10)
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!", RenderingContext.MASK_BOLD)
    print(str(context) + "\x1b[0m\n")


def demo_003():
    global context
    print('Italic')
    context = BufferedRenderingContext(10, 10)
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!", RenderingContext.MASK_ITALIC)
    print(str(context) + "\x1b[0m\n")


def demo_004():
    global context
    print('Changed default FG color')
    context = BufferedRenderingContext(10, 10)
    context.fg_color_default = 2
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!")
    print(str(context) + "\x1b[0m\n")


def demo_005():
    global context
    print('Changed default BG color')
    context = BufferedRenderingContext(10, 10)
    context.bg_color_default = 2
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!")
    print(str(context) + "\x1b[0m\n")


def demo_006():
    global context
    print('With emphasized FG')
    context = BufferedRenderingContext(10, 10)
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")


def demo_007():
    global context
    print('With emphasized FG and BG')
    context = BufferedRenderingContext(10, 10)
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED | RenderingContext.MASK_BG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")


def demo_008():
    global context
    print('With emphasized FG over custom BG color box')
    context = BufferedRenderingContext(10, 10)
    context.draw_attrs_box_at(3, 3, 5, 5, bg=(30, 40, 50))
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")


def demo_009():
    global context
    print('With emphasized FG over custom FG color box')
    context = BufferedRenderingContext(10, 10)
    context.draw_attrs_box_at(3, 3, 5, 5, fg=(130, 30, 30))
    context.cursor.seek(5, 5)
    context.draw_text("Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")


def demo_010():
    global context, context
    print('Use custom FG and BG colors to paint text')
    context = BufferedRenderingContext(10, 10)
    context.cursor.seek(5, 5)

    context.fg_color = (128, 64, 64)
    context.bg_color = (64, 128, 64)
    context.draw_text("Hello,\n")

    context.fg_color = (64, 128, 64)
    context.bg_color = (128, 64, 64)
    context.draw_text("world!")
    print(str(context) + "\x1b[0m\n")


if __name__ == '__main__':
    demo_001()
    demo_002()
    demo_003()
    demo_004()
    demo_005()
    demo_006()
    demo_007()
    demo_008()
    demo_009()
    demo_010()
