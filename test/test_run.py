import os
import unittest

import luigi
from unittest.mock import patch

import gokart


class _DummyTask(gokart.TaskOnKart):
    task_namespace = __name__
    param = luigi.Parameter()


class RunTest(unittest.TestCase):
    def setUp(self):
        luigi.configuration.LuigiConfigParser._instance = None
        os.environ.clear()

    @patch('sys.argv', new=['main', f'{__name__}._DummyTask', '--param', 'test', '--log-level=CRITICAL', '--local-scheduler'])
    def test_run(self):
        config_file_path = os.path.join(os.path.dirname(__name__), 'test_config.ini')
        luigi.configuration.LuigiConfigParser.add_config_path(config_file_path)
        os.environ.setdefault('test_param', 'test')
        with self.assertRaises(SystemExit) as exit_code:
            gokart.run()
        self.assertEqual(exit_code.exception.code, 0)

    @patch('sys.argv', new=['main', f'{__name__}._DummyTask', '--log-level=CRITICAL', '--local-scheduler'])
    def test_run_with_undefined_environ(self):
        config_file_path = os.path.join(os.path.dirname(__name__), 'test_config.ini')
        luigi.configuration.LuigiConfigParser.add_config_path(config_file_path)
        with self.assertRaises(SystemExit) as exit_code:
            with self.assertRaises(luigi.parameter.MissingParameterException) as missing_parameter:
                gokart.run()

    @patch('sys.argv', new=['main', '--tree-info', f'{__name__}._DummyTask', '--param', 'test', '--log-level=CRITICAL', '--local-scheduler'])
    def test_run_tree_info(self):
        config_file_path = os.path.join(os.path.dirname(__name__), 'test_config.ini')
        luigi.configuration.LuigiConfigParser.add_config_path(config_file_path)
        os.environ.setdefault('test_param', 'test')
        tree = gokart.run()
        self.assertTrue(gokart.make_tree_info(_DummyTask(param='test')), tree)


if __name__ == '__main__':
    unittest.main()
