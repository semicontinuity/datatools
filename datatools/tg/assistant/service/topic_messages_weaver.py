from concurrent.futures import ThreadPoolExecutor

from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.service.discussion_classifier import DiscussionClassifier


class TopicMessagesWeaver:

    def __init__(self, classifier: DiscussionClassifier) -> None:
        self.classifier = classifier
        self.executor = ThreadPoolExecutor(max_workers=1)

    def work_queue_size(self) -> int:
        return self.executor._work_queue.qsize()

    def stop(self):
        self.executor.shutdown(wait=False, cancel_futures=True)

    def _weave(self, flat_discussion: list[TgMessage]):
        self.classifier.classify_flat_discussions(flat_discussion)

    def submit(self, flat_discussion: list[TgMessage]):
        self.executor.submit(self._weave, flat_discussion)
