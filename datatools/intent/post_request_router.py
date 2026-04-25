from typing import AnyStr
import email.message

from datatools.intent.dispatcher import dispatch


def route_post_request(headers: email.message.Message, post_body: AnyStr):
    dispatch(headers, post_body)
