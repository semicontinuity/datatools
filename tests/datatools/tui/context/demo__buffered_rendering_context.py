from datatools.tui.context.buffered_rendering_context import BufferedRenderingContext
from datatools.tui.context.rendering_context import RenderingContext

if __name__ == '__main__':
    print('Regular')
    context = BufferedRenderingContext(10, 10)
    context.draw_text_at(5, 5, "Hello,\nworld!")
    print(str(context) + "\x1b[0m\n")

    print('Bold')
    context = BufferedRenderingContext(10, 10)
    context.draw_text_at(5, 5, "Hello,\nworld!", RenderingContext.MASK_BOLD)
    print(str(context) + "\x1b[0m\n")

    print('Italic')
    context = BufferedRenderingContext(10, 10)
    context.draw_text_at(5, 5, "Hello,\nworld!", RenderingContext.MASK_ITALIC)
    print(str(context) + "\x1b[0m\n")

    print('Changed default FG color')
    context = BufferedRenderingContext(10, 10)
    context.fg_color_default = 2
    context.draw_text_at(5, 5, "Hello,\nworld!")
    print(str(context) + "\x1b[0m\n")

    print('Changed default BG color')
    context = BufferedRenderingContext(10, 10)
    context.bg_color_default = 2
    context.draw_text_at(5, 5, "Hello,\nworld!")
    print(str(context) + "\x1b[0m\n")

    print('With emphasized FG')
    context = BufferedRenderingContext(10, 10)
    context.draw_text_at(5, 5, "Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")

    print('With emphasized FG and BG')
    context = BufferedRenderingContext(10, 10)
    context.draw_text_at(5, 5, "Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED | RenderingContext.MASK_BG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")

    print('With emphasized FG over custom BG color box')
    context = BufferedRenderingContext(10, 10)
    context.draw_attrs_box_at(3, 3, 5, 5, bg=(30, 40, 50))
    context.draw_text_at(5, 5, "Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")

    print('With emphasized FG over custom FG color box')
    context = BufferedRenderingContext(10, 10)
    context.draw_attrs_box_at(3, 3, 5, 5, fg=(130, 30, 30))
    context.draw_text_at(5, 5, "Hello,\nworld!", RenderingContext.MASK_FG_EMPHASIZED)
    print(str(context) + "\x1b[0m\n")
