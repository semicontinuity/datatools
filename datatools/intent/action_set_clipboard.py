import email.message
import subprocess
from typing import AnyStr


def do_set_clipboard(headers: email.message.Message, post_body: AnyStr):
    if type(post_body) is str:
        s = post_body.encode('utf-8')
    subprocess.run(['xclip', '-selection', 'clipboard'], input=post_body, stdout=subprocess.DEVNULL)
