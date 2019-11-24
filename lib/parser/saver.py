""" The save function in editor """
import lxml.html

etree = lxml.html.etree


class Saver:

    def __init__(self, serialized):
        self.serialized = serialized

        self.root = etree.Element('kmbscene')

    def _for_layer(self, feed: dict):
        layer = etree.SubElement(self.root, feed['tag'])
        layer.set('id', feed['id'])
        layer.set('x', feed['x'])
        layer.set('y', feed['y'])
        # set enter point on Input.
        if feed['class_'] == 'Input':
            layer.set('head', 'head')
        # = common area = #
        etree.SubElement(layer, 'var').text = feed['var']
        etree.SubElement(layer, 'class').text = feed['class_']
        args = etree.SubElement(layer, 'args')
        self._args_wheel(args, feed['args'])
        # ~ individual area ~ #
        etree.SubElement(layer, 'mode').text = feed['mode']
        etree.SubElement(layer, 'input').text = self.seq2str(feed['input'])
        etree.SubElement(layer, 'output').text = self.seq2str(feed['output'])

    def _for_model(self, feed):
        model = etree.SubElement(self.root, feed['tag'])
        model.set('id', feed['id'])
        model.set('x', feed['x'])
        model.set('y', feed['y'])
        # = = #
        etree.SubElement(model, 'var').text = feed['var']
        etree.SubElement(model, 'class').text = feed['class_']
        args = etree.SubElement(model, 'args')
        self._args_wheel(args, feed['args'], io_convert=True)
        # ~ ~ #
        # pass

    def _for_unit(self, feed):
        unit = etree.SubElement(self.root, feed['tag'])
        unit.set('id', feed['id'])
        unit.set('x', feed['x'])
        unit.set('y', feed['y'])
        unit.set('u', feed['type'])
        # = = #
        etree.SubElement(unit, 'var').text = feed['var']
        etree.SubElement(unit, 'class').text = feed['class_']
        args = etree.SubElement(unit, 'args')
        self._args_wheel(args, feed['args'])
        # ~ ~ #
        # pass

    def _for_ph(self, feed):
        ph = etree.SubElement(self.root, feed['tag'])
        ph.text = feed['var']
        ph.set('id', feed['id'])
        ph.set('x', feed['x'])
        ph.set('y', feed['y'])

    def _for_note(self, feed):
        note = etree.SubElement(self.root, feed['tag'])
        note.text = feed['content']
        note.set('id', feed['id'])
        note.set('x', feed['x'])
        note.set('y', feed['y'])

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

    def save_file(self, dst: str):
        self._save()
        file = etree.ElementTree(self.root)
        file.write(open(dst, 'wb'), pretty_print=True)

    # ----------UTILS----------

    @classmethod
    def seq2str(cls, seq: [list, tuple], repair_req=False):
        return ';'.join(seq) if seq else ('!REQ' if repair_req else 'null')

    @classmethod
    def _args_wheel(cls, root, args: dict, io_convert=False):
        # deliver the args to element.
        for arg_name, arg_field in args.items():
            arg_value, arg_dtype = arg_field
            arg_item = etree.SubElement(root, arg_name)
            if io_convert and arg_name in ('inputs', 'outputs'):
                # convert io sequence to string, split by `;`.
                arg_item.text = cls.seq2str(arg_field[0], repair_req=True)
            elif arg_value is None or not arg_value:
                # required value but got None instead.
                # then set a mark, means this args is required.
                arg_item.text = '!REQ'
            else:
                arg_item.text = arg_value
            arg_item.set('c', arg_dtype)
