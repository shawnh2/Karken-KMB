import os
import unittest

# set to parent directory
os.chdir(os.path.join(os.getcwd(), ".."))

from lib.auto import AutoInspector


class AutoInspectorTest(unittest.TestCase):

    def setUp(self):
        self.auto_inspector = AutoInspector()

    def test_string_type(self):
        test_type = 'String'
        t1 = self.auto_inspector.auto_type_check('te st', test_type)
        self.assertEqual(t1, 'te_st', 'string t1 error')
        t2 = self.auto_inspector.auto_type_check(' test ', test_type)
        self.assertEqual(t2, 'test', 'string t2 error')
        t3 = self.auto_inspector.auto_type_check(' te st', test_type)
        self.assertEqual(t3, 'te_st', 'string t3 error')

    def test_number_type(self):
        test_type = 'Number'
        t1 = self.auto_inspector.auto_type_check('12.34a', test_type)
        self.assertEqual(t1, '12.34', 'number t1 error')
        t2 = self.auto_inspector.auto_type_check('-12.34a45', test_type)
        self.assertEqual(t2, '-12.3445', 'number t2 error')
        t3 = self.auto_inspector.auto_type_check('12.34', test_type)
        self.assertEqual(t3, '12.34', 'number t3 error')

    def test_sequence_type(self):
        test_type = 'Sequence'
        t1 = self.auto_inspector.auto_type_check('[1,2,3,4', test_type)
        self.assertEqual(t1, '[1, 2, 3, 4]', 'seq t1 error')
        t2 = self.auto_inspector.auto_type_check('(1,2,3,4', test_type)
        self.assertEqual(t2, '(1, 2, 3, 4)', 'seq t2 error')
        t3 = self.auto_inspector.auto_type_check('1,2,3,4]', test_type)
        self.assertEqual(t3, '(1, 2, 3, 4)', 'seq t3 error')
        t4 = self.auto_inspector.auto_type_check('1,2,3,4)', test_type)
        self.assertEqual(t4, '(1, 2, 3, 4)', 'seq t4 error')
        t5 = self.auto_inspector.auto_type_check('1,2,3,4', test_type)
        self.assertEqual(t5, '(1, 2, 3, 4)', 'seq t5 error')
        t6 = self.auto_inspector.auto_type_check(')1,2,3,4,]', test_type)
        self.assertEqual(t6, '(1, 2, 3, 4)', 'seq t6 error')
        t7 = self.auto_inspector.auto_type_check('[1,2,a,3,4,)', test_type)
        self.assertEqual(t7, "[1, 2, 3, 4]", 'seq t7 error')
