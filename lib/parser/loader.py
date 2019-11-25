""" The load function in editor. """
import lxml.html

etree = lxml.html.etree


class Loader:
    """ Load XML and parse into dict. """

    def __init__(self, src_path: str):
        self.src_path = src_path
        self.content = etree.parse(self.src_path)
        self.nodes = {}  # collecting nodes

    def _gen(self):
        for node in self.content.xpath('*'):
            yield node

    def _for_layer(self, feed):
        com = self._common(feed)
        ipt = feed.xpath('input/text()')[0]
        opt = feed.xpath('output/text()')[0]
        self.nodes[com['id']] = {
            'x': com['x'],
            'y': com['y'],
            'var': com['var'],
            'cls': com['cls'],
            'arg': com['arg'],
            'type': com['type'],
            'sort': com['sort'],
            'input': ipt,
            'output': opt,
            'recover': 'node'
        }

    def _for_model(self, feed):
        com = self._common(feed)
        self.nodes[com['id']] = {
            'x': com['x'],
            'y': com['y'],
            'var': com['var'],
            'cls': com['cls'],
            'arg': com['arg'],
            'type': com['type'],
            'sort': com['sort'],
            'recover': 'node'
        }

    def _for_unit(self, feed):
        com = self._common(feed)
        self.nodes[com['id']] = {
            'x': com['x'],
            'y': com['y'],
            'var': com['var'],
            'cls': com['cls'],
            'arg': com['arg'],
            'type': com['type'],
            'sort': com['sort'],
            'recover': 'node'
        }

    def _for_ph(self, feed):
        com = self._common(feed, simplify=True)
        text = feed.xpath('./text()')[0]
        self.nodes[com['id']] = {
            'x': com['x'],
            'y': com['y'],
            'cls': 'PlaceHolder',
            'type': 'Common',
            'sort': 'Common',
            'text': text,
            'recover': 'node'
        }

    def _for_note(self, feed):
        com = self._common(feed, simplify=True)
        text = feed.xpath('./text()')[0]
        self.nodes[com['id']] = {
            'x': com['x'],
            'y': com['y'],
            'text': text,
            'recover': 'note'
        }

    def _load(self):
        for node in self._gen():
            tag = node.tag
            if tag == 'layer':
                self._for_layer(node)
            elif tag == 'model':
                self._for_model(node)
            elif tag == 'unit':
                self._for_unit(node)
            elif tag == 'ph':
                self._for_ph(node)
            elif tag == 'note':
                self._for_note(node)
            # else ...

    def load_file(self):
        self._load()
        return self.nodes

    # ----------UTILS----------

    @classmethod
    def _common(cls, feed,
                simplify=False,
                include_var=True,
                include_args=True,
                include_class=True):
        common = dict()
        # common fields have
        # id, x, y, var, cls, arg
        common['id'] = feed.xpath('./@id')[0]
        common['x'] = float(feed.xpath('./@x')[0])
        common['y'] = float(feed.xpath('./@y')[0])
        # if it's simplify, then return early.
        if simplify:
            return common
        common['type'] = feed.xpath('tp/text()')[0]
        common['sort'] = feed.xpath('sort/text()')[0]
        # for some optional kwargs.
        if include_var:
            common['var'] = feed.xpath('var/text()')[0]
        if include_class:
            common['cls'] = feed.xpath('class/text()')[0]
        if include_args:
            common['arg'] = feed.xpath('args')
        return common
