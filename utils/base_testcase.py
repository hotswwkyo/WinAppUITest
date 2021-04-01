#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/03/30 11:21:57
'''

# -*- coding:utf-8 -*-
import time
import inspect
import unittest
from .test_wrapper import testcase


class BaseTestCase(unittest.TestCase):
    """为测试类添加自动收集和自行测试用例的方法"""
    @classmethod
    def sleep(cls, seconds):

        time.sleep(seconds)
        return cls

    @classmethod
    def build_self_suite(cls):

        members = [obj_val for obj_key, obj_val in cls.__dict__.items() if inspect.ismethod(obj_val) or inspect.isfunction(obj_val)]
        test_func_list = [member for member in members if testcase.func_has_test_marker(member)]
        run_test_func_list = [tf for tf in test_func_list if testcase.get_test_marker(tf, key=testcase.ENABLED, default_value=False)]
        run_test_func_list.sort(key=lambda tf: testcase.get_test_marker(tf, key=testcase.PRIORITY, default_value=1))
        suite = unittest.TestSuite()
        for test_func in run_test_func_list:
            suite.addTest(cls(test_func.__name__))
        return suite

    @classmethod
    def run_test(cls):

        runner = unittest.TextTestRunner()
        runner.run(cls.build_self_suite())
        return runner
