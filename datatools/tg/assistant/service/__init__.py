from yndx.st.lib.llm.gradio import Gradio
from yndx.st.lib.llm.zeliboba import Zeliboba


def make_llm_provider(name: str):
    if name == 'gradio':
        return Gradio()
    elif name == 'zeliboba':
        return Zeliboba()
    else:
        raise ValueError('Unknown provider')
