""" The save function in editor """
import lxml.html

etree = lxml.html.etree


class Saver:

    def __init__(self, serialized, dst_path):
        self.serialized = serialized
        self.dst_path = dst_path

        self.root = etree.Element('kmbscene')

    def _for_layer(self, feed: dict):
        layer = etree.SubElement(self.root, feed['tag'])
        self._common_attrs(layer, feed)
        # set enter point on Input.
        if feed['class_'] == 'Input':
            layer.set('head', 'head')
        self._common_tags(layer, feed)
        # individual area.
        etree.SubElement(layer, 'mode').text = feed['mode']
        etree.SubElement(layer, 'input').text = self.seq2str(feed['input'])
        etree.SubElement(layer, 'output').text = self.seq2str(feed['output'])

    def _for_model(self, feed):
        model = etree.SubElement(self.root, feed['tag'])
        self._common_attrs(model, feed)
        self._common_tags(model, feed, include_args=False)
        # start creating its own args.
        args = etree.SubElement(model, 'args')
        self._args_wheel(args, feed['args'], io_convert=True)

    def _for_unit(self, feed):
        unit = etree.SubElement(self.root, feed['tag'])
        unit.set('u', feed['type'])
        self._common_attrs(unit, feed)
        self._common_tags(unit, feed)

    def _for_ph(self, feed):
        ph = etree.SubElement(self.root, feed['tag'])
        ph.text = feed['var']
        self._common_attrs(ph, feed)

    def _for_note(self, feed):
        note = etree.SubElement(self.root, feed['tag'])
        note.text = feed['content']
        self._common_attrs(note, feed)

    def _save(self):
        for raw in self.serialized.values():
            tag = raw['tag']
            if tag == 'layer':
                self._for_layer(raw)
            elif tag == 'model':
                self._for_model(raw)
            elif tag == 'unit':
                self._for_unit(raw)
            elif tag == 'ph':
                self._for_ph(raw)
            elif tag == 'note':
                self._for_note(raw)
            # else ...

    def save_file(self):
        self._save()
        file = etree.ElementTree(self.root)
        file.write(open(self.dst_path, 'wb'), pretty_print=True)

    # ----------UTILS----------

    @classmethod
    def seq2str(cls, seq: [list, tuple], repair_req=False):
        return ';'.join(seq) if seq else ('!REQ' if repair_req else 'null')

    @classmethod
    def _common_attrs(cls, root, feed):
        # common attrs in tag, like id, x, y
        root.set('id', feed['id'])
        root.set('x', feed['x'])
        root.set('y', feed['y'])

    def _common_tags(self,
                     root, feed,
                     include_var=True,
                     include_args=True,
                     include_class=True):
        # common tags, like tp(type), sort
        etree.SubElement(root, 'tp').text = feed['tp']
        etree.SubElement(root, 'sort').text = feed['sort']
        # some optional tags
        if include_var:
            etree.SubElement(root, 'var').text = feed['var']
        if include_class:
            etree.SubElement(root, 'class').text = feed['class_']
        if include_args:
            args = etree.SubElement(root, 'args')
            self._args_wheel(args, feed['args'])

    def _args_wheel(self, root, args: dict, io_convert=False):
        # deliver the args to element.
        for arg_name, arg_field in args.items():
            arg_value, arg_dtype = arg_field
            arg_item = etree.SubElement(root, arg_name)
            if io_convert and arg_name in ('inputs', 'outputs'):
                # convert io sequence to string, split by `;`.
                arg_item.text = self.seq2str(arg_field[0], repair_req=True)
            elif arg_value is None or not arg_value:
                # required value but got None instead.
                # then set a mark, means this args is required.
                arg_item.text = '!REQ'
            else:
                arg_item.text = arg_value
            arg_item.set('c', arg_dtype)
