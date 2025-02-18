from yndx.st.lib.llm.gradio import Gradio
from yndx.st.lib.llm.zeliboba import Zeliboba


def make_llm_provider(name: str):
    if name == 'gradio':
        return Gradio()
    elif name == 'zeliboba':
        return Zeliboba()
    else:
        raise ValueError('Unknown provider')


def message_is_short(message: str):
    return len(message) < 40


def should_summarize(message: str):
    return ('\n' in message and len(message) > 40) or len(message) > 120