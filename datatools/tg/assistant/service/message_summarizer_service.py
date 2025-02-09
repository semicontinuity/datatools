from yndx.st.lib.llm.zeliboba import Zeliboba

from datatools.tg.assistant.model.tg_data import TgData


class MessageSummarizer:
    llm: Zeliboba
    tg_data: TgData

    def __init__(self, tg_data: TgData) -> None:
        self.llm = Zeliboba(model_name=None)
        self.tg_data = tg_data

    def start(self):
        for channel_data in self.tg_data.tg_channels:
            for tg_topic in channel_data.tg_topics:
                pass
