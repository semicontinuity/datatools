def message_is_short(message: str):
    return len(message) < 40


def should_summarize(message: str):
    return ('\n' in message and len(message) > 40) or len(message) > 120