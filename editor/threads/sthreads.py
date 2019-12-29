""" Searching thread """
from PyQt5.QtCore import QThread

from lib import blur_query
from editor.widgets.search_bar import KMBSearchBar


class SearchBarThread(QThread):
    """ A thread for search bar and its dependencies. """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_bar = KMBSearchBar(parent,
                                       SearchingThread())
        self.callbacks = []
        self.view = parent
        self.coords = [0, -300]
        self.step = 100
        self.stack = 5  # stack number
        self.cur_stack = 0
        # init slots
        self.search_bar.search_body.ENTER_NEW_ITEM.connect(self.new_node)

    def __call__(self, *callbacks):
        # if have args, use tuple here.
        self.callbacks = callbacks
        self.run()

    def is_display(self):
        return self.search_bar.on_display

    def new_node(self, name: str, sort: str, category: str, args: str):
        # also change the coords every time making new node.
        if self.cur_stack >= self.stack:
            self.coords[0] += abs(self.step)
            self.step *= -1
            self.cur_stack = 1
        else:
            self.coords[1] += self.step
            self.cur_stack += 1
        # candies are made of repeating nbr and args string.
        self.view.add_node(name, sort, category, args, self.coords)

    def run(self):
        # run all the callbacks here.
        for callback in self.callbacks:
            if isinstance(callback, tuple):
                call, *args = callback
                call(*args)
            else:
                callback()

    # ------CALLBACKS------

    def cb_slide_in(self):
        self.search_bar.slide_in_animation()

    def cb_slide_out(self):
        self.search_bar.slide_out_animation()

    def cb_set_size(self, width, height):
        self.search_bar.update_size(width, height)


class SearchingThread(QThread):
    """ A thread only for searching process. """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_word: str = None
        self.query_results = []
        self.query_candies = None

    def search(self, query_word: str) -> int:
        self.query_word = query_word
        self.run()
        # return the count of results.
        return len(self.query_results)

    def _search_candy(self):
        """
        Some grammar in query line edit.

        QUERY(:NUMBER);ARG=VALUE;[...]
        eg: dense(:3);units=64;[...] (etc.)

        also with auto complete function.
        if the typing arg is not exist, then will pass it.
        """
        query = self.query_word.replace(' ', '').split(';', 1)
        word, *args = query
        # :N candy
        nbr = 1
        if ':' in word:
            query, nbr = word.split(':')
            self.query_word = query
            nbr = int(nbr) if nbr.isdigit() else 1
        # [ARG; [...]] candy
        args = args[0] if args else 'None'
        self.query_candies = (nbr, args)

    def clean(self):
        self.query_word = None
        self.query_results = []
        self.query_candies = None

    def fetchall(self):
        # a generator that fetch all query results.
        for result in self.query_results:
            # also highlight the key word.
            from_idx = result[0].lower().index(self.query_word)
            yield result, from_idx, len(self.query_word)
        # clean all after fetching.
        self.clean()

    def fetch_candies(self):
        return self.query_candies

    def run(self):
        self._search_candy()
        self._query_database()

    def _query_database(self):
        # do query through database.
        # fields: name, info, sort, category
        self.query_results += blur_query(self.query_word)

    def _query_stack(self):
        # do query through history stack.
        pass
