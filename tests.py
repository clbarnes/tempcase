import os
import tempfile
import unittest

from tempcase import TempCase, in_tempdir

TMP = tempfile.gettempdir()


def cls_assert_set_equal(set1, set2):
    """Because in py2, assertSetEqual can only be called as an instance method"""
    assert isinstance(set1, set), 'set1 is not a set'
    assert isinstance(set2, set), 'set2 is not a set'
    assert set1 == set2, '''
Extra items in set1:
    {}
Extra items in set2: 
    {}
'''.format(set1-set2, set2-set1).strip()


class TempCaseTests(TempCase):
    _project_name = 'tempcase'

    @staticmethod
    def tmp_contents():
        return set(os.listdir(TMP))

    def class_contents(self):
        return set(os.listdir(self._output_root))

    @classmethod
    def setUpClass(cls):
        cls.before_cls_items = cls.tmp_contents()
        super(TempCaseTests, cls).setUpClass()

    def class_diff(self):
        return self.tmp_contents() - self.before_cls_items

    def test_dir_names(self):
        path = self.path_to()
        basename, method_dir = os.path.split(path)
        self.assertTrue(self._testMethodName in method_dir)
        basename, class_dir = os.path.split(basename)
        for element in ['tempcase', type(self).__name__, ':', '-']:
            self.assertTrue(element in class_dir)

    def test_cls_dir_created_and_cleaned_up(self):
        path = self.path_to_cls()
        self.assertTrue(path.startswith(TMP))
        self.assertTrue(os.path.exists(path))
        self.assertSetEqual(self.class_contents(), set())

    def test_method_dir_created_and_cleaned_up(self):
        path = self.path_to()
        self.assertTrue(path.startswith(TMP))
        self.assertTrue(os.path.exists(path))
        self.assertTrue(len(self.class_contents()) == 1)

    def test_file_created_and_cleaned_up(self):
        path = self.path_to('file.txt')
        open(path, 'w').close()
        self.assertTrue(path.startswith(TMP))
        self.assertTrue(os.path.exists(path))
        self.assertTrue(len(self.class_contents()) == 1)

    @classmethod
    def tearDownClass(cls):
        super(TempCaseTests, cls).tearDownClass()
        cls_assert_set_equal(cls.before_cls_items, cls.tmp_contents())


class InTempdirTests(unittest.TestCase):
    def setUp(self):
        self.assertFalse(os.getcwd().startswith(TMP))

    def test_no_decoration(self):
        self.assertFalse(os.getcwd().startswith(TMP))

    @in_tempdir('tempcase')
    def test_decoration_cd(self):
        self.assertTrue(os.getcwd().startswith(TMP))

    @in_tempdir('tempcase')
    def test_decoration_dirname(self):
        for element in ['tempcase', type(self).__name__, self._testMethodName, ':', '-']:
            self.assertTrue(element in os.getcwd())

    def tearDown(self):
        self.assertFalse(os.getcwd().startswith(TMP))


# todo: test cleanup prevention, somehow
