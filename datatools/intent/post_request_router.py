from datatools.intent.dispatcher import dispatch


def route_post_request(headers, post_body):
    dispatch(headers, post_body)
