from concurrent.futures import ThreadPoolExecutor

from yndx.st.lib.llm.zeliboba import Zeliboba

from datatools.tg.assistant.model.tg_message import TgMessage


class MessageSummarizerService:
    llm: Zeliboba

    def __init__(self) -> None:
        import warnings, urllib3
        warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

        self.llm = Zeliboba(model_name=None)
        self.executor = ThreadPoolExecutor(max_workers=2)

    def stop(self):
        self.executor.shutdown(wait=False, cancel_futures=True)

    def _summarize(self, tg_message: TgMessage):
        r = self.llm.invoke(
            system_message="""
Сделай заголовок для текста, наподобие темы e-mail. Без кавычек. Включай к заголовок важные детали.

Примеры:

===
Вчера включили новые юниты на нашего клиента на тестинге + продолжала заниматься табом расписания

Сегодня, видимо, день встреч и обсуждения накопившихся вопросов по редизайну)
---
Вчера включили новые юниты, таб расписания. Сегодня встречи, обсуждение редизайна.
===
а вот это помогло. Спасибо!
Видимо я до смены ноута такую настройку уже делал, но при переезде не скопировалось вместе с экспортом настроек
---
Настройки ноута - проблема решена
===
Release Plarform #999 выкатываю в прод VLA
---
Release Platform #999 -> prod VLA
===
platform cloud release #729 после триала докачу в прод
---
План: platform cloud release #729 -> prod
===
Platform #1005
Platform Core #1855
могу выкатить в препрод?
@user
---
Platform #1005, Platform Core #1855 -> preprod?
===
Plarform #1005 в препроде упал по таймауту
Successful call to next operator: first operator is unavailable
https://sandbox.yandex-team.ru/task/2962443980/build_report
@user
---
Plarform #1005 (preprod), таймаут ("first operator is unavailable")
===
Коллеги,, получил несколько обращений по проблеме загрузки статистики в Системе,, падала в ошибку,
прислали скрины,, от себя проблему не могу воспроизвести.
Не подскажите были ли какие то инциденты сегодня которые могли повлиять на это? @user
---
Проблема с загрузкой статистики в Системе. Сегодня были инциденты?
===
@user а какой мы считаем вес у функциональности страницы ABC?
Если она не отвечает, то на сколько процентов сервис лежит?
---
Вес функциональности страницы ABC?
""",
            user_message=tg_message.message
        )
        tg_message.ext.summary = r

    def request_summary(self, tg_message: TgMessage):
        self.executor.submit(self._summarize, tg_message)
