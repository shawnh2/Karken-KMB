""" The save function in editor """
import lxml.html

etree = lxml.html.etree


class Saver:

    def __init__(self, serialized):
        self.serialized = serialized

        self.root = etree.Element('kmbscene')
        self.root.set('name', 'YOUR NAME')

    # TODO: some arg that choose from combobox, may be str rather than id.

    def _for_layer(self, feed: dict):
        layer = etree.SubElement(self.root, feed['tag'])
        layer.set('id', feed['id'])
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
            # else ...

    def save_file(self, dst="parser/test_save.xml"):
        self._save()
        file = etree.ElementTree(self.root)
        file.write(open(dst, 'wb'), pretty_print=True)

    # ----------UTILS----------

    @classmethod
    def seq2str(cls, seq: [list, tuple]):
        return ';'.join(seq) if seq else 'null'

    @classmethod
    def _args_wheel(cls, root, args: dict, io_convert=False):
        # deliver the args to element
        for arg_name, arg_field in args.items():
            # arg_value, arg_dtype = arg_field
            arg_item = etree.SubElement(root, arg_name)
            if io_convert and arg_name in ('inputs', 'outputs'):
                # convert io sequence to string, split by `;`
                arg_item.text = cls.seq2str(arg_field[0])
            else:
                arg_item.text = arg_field[0]
            arg_item.set('c', arg_field[1])
