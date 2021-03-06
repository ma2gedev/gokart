import unittest
from unittest.mock import patch, MagicMock

import luigi
import luigi.mock
import gokart
import gokart.info


class _SubTask(gokart.TaskOnKart):
    task_namespace = __name__
    param = luigi.IntParameter()

    def output(self):
        return self.make_target('sub_task.txt')

    def run(self):
        self.dump(f'task uid = {self.make_unique_id()}')


class _Task(gokart.TaskOnKart):
    task_namespace = __name__
    param = luigi.IntParameter(default=10)
    sub = gokart.TaskInstanceParameter(default=_SubTask(param=20))

    def requires(self):
        return self.sub

    def output(self):
        return self.make_target('task.txt')

    def run(self):
        self.dump(f'task uid = {self.make_unique_id()}')


class TestInfo(unittest.TestCase):
    @patch('luigi.LocalTarget', new=lambda path, **kwargs: luigi.mock.MockTarget(path, **kwargs))
    def test_make_tree_info(self):
        task = _Task(param=1, sub=_SubTask(param=2))

        # check before running
        tree = gokart.info.make_tree_info(task)
        expected = """
└─-(PENDING) _Task[e184cb7ec714433df0c9961a4d309c03]
   └─-(PENDING) _SubTask[349cae3865f560bf5596e7cad426babd]"""
        self.assertEqual(expected, tree)

        # check after sub task runs
        luigi.build([task], local_scheduler=True, log_level='CRITICAL')
        tree = gokart.info.make_tree_info(task)
        expected = """
└─-(COMPLETE) _Task[e184cb7ec714433df0c9961a4d309c03]
   └─-(COMPLETE) _SubTask[349cae3865f560bf5596e7cad426babd]"""
        self.assertEqual(expected, tree)

        # check tree with details
        task.get_processing_time = MagicMock(return_value=2.)
        task.sub.get_processing_time = MagicMock(return_value=3.)
        task.task_log['test'] = 'task log'
        tree = gokart.info.make_tree_info(task, details=True)
        expected = """
└─-(COMPLETE) _Task[e184cb7ec714433df0c9961a4d309c03](parameter={'workspace_directory': './resources/', 'local_temporary_directory': './resources/tmp/', 'param': '1', 'sub': '_SubTask-349cae3865f560bf5596e7cad426babd'}, output=['./resources/task_e184cb7ec714433df0c9961a4d309c03.txt'], time=2.0s, task_log={'test': 'task log'})
   └─-(COMPLETE) _SubTask[349cae3865f560bf5596e7cad426babd](parameter={'workspace_directory': './resources/', 'local_temporary_directory': './resources/tmp/', 'param': '2'}, output=['./resources/sub_task_349cae3865f560bf5596e7cad426babd.txt'], time=3.0s, task_log={})"""
        self.assertEqual(expected, tree)


if __name__ == '__main__':
    unittest.main()
