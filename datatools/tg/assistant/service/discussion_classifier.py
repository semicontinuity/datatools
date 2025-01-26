import re
import sys
from sortedcontainers import SortedDict
from gradio_client import Client

from datatools.tg.assistant.model.tg_message import TgMessage


class DiscussionClassifier:
    PROMPT = """
You are a helpful assistant.

You are given a list of phrases from a chat. Every phrase will have an ID before it.
Phrases can belong to several conversations.
Conversations can be composed of consecutive phrases, or overlapping - so that multiple conversations take place simultaneously.
Relate phrases to each other.

Your task is to output the ID of phrase and ID of phrase, where the conversation has started.
Output only the list of ID pairs, do not provide any explanations.

Example output:
#####
123 123
124 123
125 123
126 126
127 123
#####
"""

    PROMPT2 = """
You are a helpful assistant.

You are given a list of phrases from a chat.
Phrases can belong to several concurrent conversations.

Before every phrase, there is a header with format "ID=[ID of the phrase] FOLLOWS_ID=[ID of the phrase that is replies to or follows logically]".
If FOLLOWS_ID is unknown, it is specified as "<INFER>".

The task is: for a phrase, infer its logically preceding phrase, use its ID for FOLLOWS_ID,
and output a line with the same format "ID=[ID of the phrase] FOLLOWS_ID=[ID of the phrase that is replies to or follows logically]".
Typically, the logically preceding phrase is close enough.
   
If the preceding phrase cannot be resolved, or you are not sure, retain "<INFER>" for the value of FOLLOWS_ID.

Do not provide any explanations. Output only for *unknown* values of FOLLOWS_ID. 


Example input:

#####
ID=120 FOLLOWS_ID=<INFER>

планирую запустить прокси
- сначала abc
- потом def
#####
ID=121 FOLLOWS_ID=120

займусь запуском прокси
- сначала abc
- потом def
или отложим на след. неделю?
#####
ID=122 FOLLOWS_ID=<INFER>

можно и сейчас, если время есть.
#####
ID=123 FOLLOWS_ID=<INFER>

после прогона CI, 5 проблем для бэка, 55 для фронта
#####
ID=124 FOLLOWS_ID=123

По поводу 55 проблем я посылал письмо.
Возможно, это из-за сети.
#####
ID=125 FOLLOWS_ID=<INFER>

Половина инстансов envoy недоступна. Может, забыли поднять?
#####
ID=126 FOLLOWS_ID=<INFER>

Может, ещё раз попробовать?
#####
ID=127 FOLLOWS_ID=<INFER>

Что касается проблем бэка - это повторяется уже неделю


Example output:

ID=120 FOLLOWS_ID=<INFER>
ID=122 FOLLOWS_ID=121
ID=123 FOLLOWS_ID=<INFER>
ID=125 FOLLOWS_ID=<INFER>
ID=126 FOLLOWS_ID=123
ID=127 FOLLOWS_ID=123
"""


    #             * Next phrase in the topic indicates some action applicable to the current state of the subject of the thread (e.g. "I'm starting xyz" - "Stop!")
    # OR multiple candidates could fit

    PROMPT3 = """
Role: You are a conversation threading analyzer.
Task: Link phrases to their logical predecessors in multi-threaded chats.
Input Format:

    Each phrase has a header:
    FROM=[user] ID=[number] FOLLOWS_ID=[number|<INFER>]

    Phrase IDs are increasing numbers, that reflect temporal order of phases.
    <INFER> means the predecessor is unknown and needs to be determined.

Instructions:

    Analyze Context:

        * Treat phrases as part of concurrent conversations (threads).
        * Identify threads by topic continuity (i.e., phrases within the topic form a consistent conversation).
        * If FOLLOWS_ID is known (is a number), then the predecessor of the phrase has ID equal FOLLOWS_ID.
        
        * Key indicators of topic continuity:
            * **Question-Answer Chains**: Prioritize links where a phrase directly answers a question (e.g., "Should we X?" → "Yes, let’s do X").
            * **Same-User Temporal Proximity**: Temporally close phrases from the same user are likely to be in the same thread (follow-up). Prioritize linking, if there is no contradiction.
            * **Temporal Proximity**: Default to the immediately preceding message if no contradictions exist (answers like "Ок" often follow their question).
        
        * Other indicators of topic continuity (the more matches, the more likely is the topic continuity):
            * Next phrase in the topic can shares some domain-specific keywords, user earlier in the thread
            * Next phrase in the topic can contribute to the topic of the thread (e.g. continues a task list)
            * Next phrase in the topic can suggest some alternative (e.g. "Should we do xyz now?" - "Okay, but let's do it later")
            * Next phrase in the topic can reason about the subject of the topic  (e.g. "We could add some resources" - "Well, there is enough CPU")
            * Next phrase in the topic can have linguistic cues (e.g., "on the subject of ..." refers to prior mention of the subject in the thread)

    Link Phrases:
      For each <INFER> phrase:
        * Resolve **question-answer pairs first**, even without shared keywords.
        * Find the most recent ID in the same thread that directly precedes it temporally (thread predecessor)
        * If no clear match exists, retain <INFER>.

    Output Rules:
        * Only output lines where FOLLOWS_ID was originally <INFER>.
        * Never modify already resolved IDs (e.g., FOLLOWS_ID=120 stays unchanged).
        * Strictly use format: ID=X FOLLOWS_ID=Y (one line per inferred ID).


Example:

Input (simplified):


#####
FROM=user1 ID=120 FOLLOWS_ID=<INFER>

планирую запустить прокси
- сначала abc
- потом def
#####
ID=121 FOLLOWS_ID=120

FROM=user1 займусь запуском прокси
- сначала abc
- потом def
или отложим на след. неделю?
@user2
#####
ID=122 FOLLOWS_ID=<INFER>

FROM=user2 можно и сейчас, если время есть.
#####
ID=123 FOLLOWS_ID=<INFER>

FROM=user3 после прогона CI, 5 проблем для бэка, 55 для фронта
#####
FROM=user4 ID=124 FOLLOWS_ID=<INFER>

По поводу 55 проблем я посылал письмо.
Возможно, это из-за сети.
#####
FROM=user6 ID=125 FOLLOWS_ID=<INFER>

Половина инстансов envoy недоступна. Может, забыли поднять?
#####
FROM=user7 ID=126 FOLLOWS_ID=<INFER>

Может, ещё раз попробовать?
#####
FROM=user8 ID=127 FOLLOWS_ID=<INFER>

Что касается проблем бэка - это повторяется уже неделю
#####
FROM=user8 ID=128 FOLLOWS_ID=<INFER>

@user1


Output:

ID=120 FOLLOWS_ID=<INFER>
ID=122 FOLLOWS_ID=121
ID=123 FOLLOWS_ID=<INFER>
ID=124 FOLLOWS_ID=<INFER>
ID=125 FOLLOWS_ID=<INFER>
ID=126 FOLLOWS_ID=123
ID=127 FOLLOWS_ID=123
ID=128 FOLLOWS_ID=127


Your Turn:

Process the provided phrases. Only output updated <INFER> lines.
No explanations. Maintain original language/formatting.
"""

    PROMPT3_RE = re.compile('ID=(\\d+) FOLLOWS_ID=([\\d+]+)')

    def __init__(self) -> None:
        self.client = Client("Qwen/Qwen2.5", verbose=False)

    def classify(self, raw_discussions: list[TgMessage]) -> list[TgMessage]:
        flat_discussions = self.flat_discussions(raw_discussions)
        query = self.classify_query_discussions_part2(flat_discussions)

        print(f'Classifying discussions', file=sys.stderr)
        print('', file=sys.stderr)
        print(query, file=sys.stderr)

        r1, r2, r3 = self.client.predict(
            api_name="/model_chat_1",
            radio="72B",
            system=DiscussionClassifier.PROMPT3,
            query=query,
        )
        response_text = r2[0][1]['text']

        # return response_text
        print(response_text, file=sys.stderr)
        starters = self.parse_starters_llm_response_prompt_3(response_text)
        return self.weave_discussions(flat_discussions, starters)

    def classify0(self, raw_discussions: list[TgMessage]) -> list[TgMessage]:
        starters = self.parse_starters_llm_response(
            '#####\n48868 48868\n48915 48868\n48922 48922\n48935 48922\n48939 48922\n48942 48922\n48943 48942\n48944 48942\n48945 48942\n48946 48922\n48947 48946\n48960 48960\n48965 48965\n48966 48965\n48967 48965\n48989 48989\n48992 48989\n48995 48989\n48998 48998\n49013 48922\n49023 48965\n#####'
        )
        return self.weave_discussions(raw_discussions, starters)

    @staticmethod
    def weave_discussions(flat_discussions: list[TgMessage], starters: dict[int, int]) -> list[TgMessage]:
        """
        :param flat_discussions: list of raw discussions (every item is top-level TgMessage, not a reply)
        """
        discussions: dict[int, TgMessage] = {d.id: d for d in flat_discussions}

        # Use 'starters' to weave together discussions
        for d_id, starter_id in starters.items():
            print(f'NEED LINK {d_id} to {starter_id}', file=sys.stderr)
            if d_id == starter_id:
                continue
            super_discussion = discussions.get(starter_id)
            discussion = discussions.get(d_id)

            if not discussion or not super_discussion:
                # LLM has missed
                continue

            super_discussion.replies[d_id] = discussion
            discussion.is_attached = True

        return [d for d in discussions.values() if not d.is_attached and not d.is_reply_to]

    def parse_starters_llm_response(self, text) -> dict[int, int]:
        lines = text.splitlines()
        starters = {}
        for line in lines:
            if '#' in line.strip():
                continue
            key, value = line.split()
            starters[int(key)] = int(value)
        return starters

    def parse_starters_llm_response_prompt_3(self, text) -> dict[int, int]:
        lines = text.splitlines()
        starters = {}
        for line in lines:
            m = DiscussionClassifier.PROMPT3_RE.search(line)
            if m:
                key = m.group(1)
                value = m.group(2)
                starters[int(key)] = int(value)
        return starters

    def classify_query_discussions_part(self, raw_discussions: list[TgMessage]):
        return '\n'.join([
            f"""        
#####
{self.to_structured_string(d)}

"""
            for d in raw_discussions
        ])

    def to_structured_string(self, m: TgMessage, indent: int = 0):
        res = f'{m.id}\n\n' if not indent else ''
        res += "\n".join([(' ' * (indent - 2) + '| ' if indent else '') + s for s in m.message.split('\n')])
        if m.replies:
            res += ''.join('\n\n' + self.to_structured_string(r, indent + 2) for r in m.replies.values())
        return res

    def classify_query_discussions_part2(self, flat_discussions: list[TgMessage]):
        if len(flat_discussions) == 0:
            return ''

        return '\n'.join([self._tg_message(item) for item in flat_discussions])

    def flat_discussions(self, raw_discussions):
        items: SortedDict[int, 'TgMessage'] = SortedDict()

        for raw_discussion in raw_discussions:
            self.classify_query_discussions_part2_add_to(items, raw_discussion)

        return list(items.values())

    def classify_query_discussions_part2_add_to(self, res: SortedDict[int, 'TgMessage'], m: TgMessage):
        res[m.id] = m
        for reply in m.replies.values():
            self.classify_query_discussions_part2_add_to(res=res, m=reply)

    def _tg_message(self, m: TgMessage):
        return f"""
#####
FROM={m.get_username()} ID={m.id} FOLLOWS_ID={m.is_reply_to if m.is_reply_to else "<INFER>"}

{m.message}
"""