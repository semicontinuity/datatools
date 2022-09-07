from datatools.tui.context.buffered_rendering_context import Buffer
from datatools.tui.context.rendering_context import AbstractBuffer


def demo_001():
    print('Regular')
    buffer = Buffer(10, 10)
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!")
    print(str(buffer) + "\x1b[0m\n")


def demo_002():
    print('Bold')
    buffer = Buffer(10, 10)
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!", AbstractBuffer.MASK_BOLD)
    print(str(buffer) + "\x1b[0m\n")


def demo_003():
    print('Italic')
    buffer = Buffer(10, 10)
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!", AbstractBuffer.MASK_ITALIC)
    print(str(buffer) + "\x1b[0m\n")


def demo_004():
    print('Changed default FG color')
    buffer = Buffer(10, 10)
    buffer.fg_color_default = 2
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!")
    print(str(buffer) + "\x1b[0m\n")


def demo_005():
    print('Changed default BG color')
    buffer = Buffer(10, 10)
    buffer.bg_color_default = 2
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!")
    print(str(buffer) + "\x1b[0m\n")


def demo_006():
    print('With emphasized FG')
    buffer = Buffer(10, 10)
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!", AbstractBuffer.MASK_FG_EMPHASIZED)
    print(str(buffer) + "\x1b[0m\n")


def demo_007():
    print('With emphasized FG and BG')
    buffer = Buffer(10, 10)
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!", AbstractBuffer.MASK_FG_EMPHASIZED | AbstractBuffer.MASK_BG_EMPHASIZED)
    print(str(buffer) + "\x1b[0m\n")


def demo_008():
    print('With emphasized FG over custom BG color box')
    buffer = Buffer(10, 10)
    buffer.draw_attrs_box_at(3, 3, 5, 5, bg=(30, 40, 50))
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!", AbstractBuffer.MASK_FG_EMPHASIZED)
    print(str(buffer) + "\x1b[0m\n")


def demo_009():
    print('With emphasized FG over custom FG color box')
    buffer = Buffer(10, 10)
    buffer.draw_attrs_box_at(3, 3, 5, 5, fg=(130, 30, 30))
    writer = buffer.cursor
    writer.seek(5, 5)
    writer.draw_text("Hello,\nworld!", AbstractBuffer.MASK_FG_EMPHASIZED)
    print(str(buffer) + "\x1b[0m\n")


def demo_010():
    print('Use custom FG and BG colors to paint text')
    buffer = Buffer(10, 10)
    writer = buffer.cursor
    writer.seek(5, 5)

    writer.fg_color = (128, 64, 64)
    writer.bg_color = (64, 128, 64)
    writer.draw_text("Hello,\n")

    writer.fg_color = (64, 128, 64)
    writer.bg_color = (128, 64, 64)
    writer.draw_text("world!")
    print(str(buffer) + "\x1b[0m\n")


def demo_011():
    print('Tab')
    buffer = Buffer(20, 10)
    writer = buffer.cursor
    writer.seek(1, 1)
    writer.draw_text("Hello\tworld")
    print(str(buffer) + "\x1b[0m\n")


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
    demo_011()
