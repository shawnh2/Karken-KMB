""" Searching thread """
from PyQt5.QtCore import QThread

from lib import blur_query


class SearchingThread(QThread):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_word: str = None
        self.query_results = []

    def search(self, query_word: str) -> int:
        self.query_word = query_word
        self.run()
        # return the count of results.
        return len(self.query_results)

    def clean(self):
        self.query_word = None
        self.query_results = []

    def fetchall(self):
        # a generator that fetch all query results.
        for result in self.query_results:
            # also highlight the key word.
            from_idx = result[0].lower().index(self.query_word)
            yield result, from_idx, len(self.query_word)
        # clean all after fetching.
        self.clean()

    def run(self):
        self._query_database()

    def _query_database(self):
        # do query through database.
        # fields: name, info, sort, category
        self.query_results += blur_query(self.query_word)

    def _query_stack(self):
        # do query through history stack.
        pass
