import re
import sys

from yndx.st.lib.llm import LargeLanguageModel

from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.service.discussion_forest_flattener import flat_discussion_forest


class DiscussionClassifier:

    PROMPT3 = """
Role: You are a conversation threading analyzer.
Task: Link phrases to their logical predecessors in multi-threaded chats.
Input Format:

    Each phrase has a header:
    FROM=[user] ID=[number] FOLLOWS_ID=[number|<INFER>]

    Phrase IDs are INCREASING numbers, that reflect temporal order of phases.
    <INFER> means the predecessor is unknown and needs to be determined.

Instructions:

    Analyze Context:

        * Treat phrases as part of concurrent conversations (threads).
        * Phrase IDs are increasing in every thread. 
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
        * Find the most recent ID in the same thread that directly PRECEDES it temporally (thread predecessor). Search only in preceding phrases.
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
FROM=user1 ID=121 FOLLOWS_ID=120

займусь запуском прокси
- сначала abc
- потом def
или отложим на след. неделю?
@user2

#####
FROM=user2 ID=122 FOLLOWS_ID=<INFER>

можно и сейчас, если время есть.

#####
FROM=user3 ID=123 FOLLOWS_ID=<INFER>

после прогона CI, 5 проблем для бэка, 55 для фронта

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
Provide no explanations. Maintain original language/formatting.
"""

    PROMPT3_RE = re.compile('ID=(\\d+) FOLLOWS_ID=([\\d+]+)')

    def __init__(self, llm: LargeLanguageModel) -> None:
        self.llm = llm

    def classify(self, discussion_forest: list[TgMessage]) -> list[TgMessage]:
        if len(discussion_forest) == 0:
            return discussion_forest

        return self.classify_flat_discussions(flat_discussion_forest(discussion_forest))

    def classify_flat_discussions(self, flat_discussions):
        query = self.classify_discussions_query_data(flat_discussions)
        print(f'Classifying discussions', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'', file=sys.stderr)
        print(query, file=sys.stderr)
        print(f'', file=sys.stderr)
        print(f'', file=sys.stderr)
        response_text = self.llm.invoke(DiscussionClassifier.PROMPT3, query)
        print(response_text, file=sys.stderr)
        starters = self.parse_starters_llm_response(response_text)
        return self.weave_discussions(flat_discussions, starters)

    @staticmethod
    def weave_discussions(flat_discussions: list[TgMessage], starters: dict[int, int]) -> list[TgMessage]:
        """
        :param flat_discussions: list of raw discussions (every item is top-level TgMessage, not a reply)
        """
        print('weave_discussions: ', len(flat_discussions), file=sys.stderr)
        discussions: dict[int, TgMessage] = {d.id: d for d in flat_discussions}

        for d in flat_discussions:
            # Empty array is marker: inference is done
            if d.ext.inferred_replies is None:
                d.ext.inferred_replies = []

        # Use 'starters' to weave together discussions
        for d_id, starter_id in starters.items():
            print(f'NEED LINK {d_id} to {starter_id}', file=sys.stderr)
            if d_id == starter_id:
                print('WRONG', file=sys.stderr)
                continue

            if d_id < starter_id:
                print('WRONG', file=sys.stderr)
                # UGLY workaround! should not happen!
                d_id, starter_id = starter_id, d_id
            super_discussion: TgMessage = discussions.get(starter_id)
            discussion = discussions.get(d_id)

            if not discussion or not super_discussion:
                # LLM has missed
                continue

            if discussion.id in super_discussion.replies:
                print(f'ALREADY IN REPLIES: {d_id} in replies of {starter_id}', file=sys.stderr)
                continue

            super_discussion.ext.inferred_replies.append(d_id)
            super_discussion.ext.inferred_replies.sort()
            discussion.ext.is_inferred_reply_to = starter_id

            # super_discussion.replies[d_id] = discussion
            print(f'ADDED {d_id} as REPLY to {starter_id}', file=sys.stderr)
            # discussion.ext.is_attached = True

        # return [d for d in discussions.values() if not d.ext.is_attached and not d.ext.is_reply_to]
        return [d for d in flat_discussions if not d.ext.is_inferred_reply_to and not d.ext.is_reply_to]

    def parse_starters_llm_response(self, text) -> dict[int, int]:
        lines = text.splitlines()
        starters = {}
        for line in lines:
            m = DiscussionClassifier.PROMPT3_RE.search(line)
            if m:
                key = m.group(1)
                value = m.group(2)
                starters[int(key)] = int(value)
        return starters

    def classify_discussions_query_data(self, flat_discussions: list[TgMessage]):
        if len(flat_discussions) == 0:
            return ''

        return '\n'.join([self._tg_message(item) for item in flat_discussions])

    def _tg_message(self, m: TgMessage):
        if m.ext.is_reply_to:
            replies_to = m.ext.is_reply_to
        elif m.ext.is_inferred_reply_to:
            replies_to = m.ext.is_inferred_reply_to
        else:
            replies_to = '<INFER>'

        return f"""
#####
FROM={m.get_username()} ID={m.id} FOLLOWS_ID={replies_to}

{m.message}
"""
