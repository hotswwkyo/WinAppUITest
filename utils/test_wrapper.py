#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/03/30 11:17:36
'''
import inspect
import functools


class Test(object):
    """用于标记方法为测试用例"""

    ALWAY_RUN = 'alway_run'
    ENABLED = 'enabled'
    PRIORITY = 'priority'
    DATA_PROVIDER = 'data_provider'
    DATA_PROVIDER_CLASS = 'data_provider_class'
    DESCRIPTION = 'description'
    GROUPS = 'groups'
    MARKER = 'test_settings'

    DEFAULT_SETTTINGS = {
        ALWAY_RUN: False,
        DATA_PROVIDER: None,
        DATA_PROVIDER_CLASS: None,
        'depends_on_groups': [],
        'depends_on_methods': [],
        DESCRIPTION: '',
        ENABLED: True,
        GROUPS: [],
        PRIORITY: 1,
    }

    def __init__(self, **settings):
        """

        Args:

        """

        self.settings = {k: v for k, v in self.DEFAULT_SETTTINGS.items()}
        self.settings.update(settings)

    def _get_datas(self, data_provider_class, data_provider_method_name):

        provider = data_provider_class()
        provider_method = getattr(provider, data_provider_method_name)
        if provider_method:
            if inspect.ismethod(provider_method) or inspect.isfunction(provider_method):
                return provider_method()
            else:
                raise TypeError('{}必须是一个可调用的方法'.format(data_provider_method_name))
        else:
            raise ValueError('类({0})不存在该方法: {1}'.format(data_provider_class.__name__, data_provider_method_name))

    def __call__(self, func):

        func_name = func.__name__
        argspec = inspect.getfullargspec(func)
        setattr(func, self.MARKER, self.settings)

        @functools.wraps(func)
        def _call(*args, **kwargs):

            instance = args[0] if len(args) > 0 else None
            method_instance = instance if instance and self.is_method_instance(instance, func_name) else None
            new_args = list(args)
            pos_args_len = len(argspec.args)
            pos_varargs_len = 1 if argspec.varargs else 0
            insert_data = False
            insert_pos_index = 0

            if pos_varargs_len < 0:
                if pos_args_len < 0:
                    insert_data = False
                elif pos_args_len < 2:
                    if method_instance:
                        insert_data = False
                    else:
                        insert_data = True
                        insert_pos_index = 0
                else:
                    insert_data = True
                    if method_instance:
                        insert_pos_index = 1
                    else:
                        insert_pos_index = 0
            else:
                insert_data = True
                if method_instance:
                    insert_pos_index = 1
                else:
                    insert_pos_index = 0
            if insert_data:
                class_obj = self.settings.get(self.DATA_PROVIDER_CLASS)
                method_name = self.settings.get(self.DATA_PROVIDER)
                if (class_obj and inspect.isclass(class_obj)) and (method_name and isinstance(method_name, str)):
                    new_args.insert(insert_pos_index, self._get_datas(class_obj, method_name))
            return func(*tuple(new_args), **kwargs)

        return _call

    def is_method_instance(self, instance, method_name):
        return inspect.ismethod(getattr(instance, method_name))

    @classmethod
    def func_has_test_marker(cls, obj):

        if inspect.ismethod(obj) or inspect.isfunction(obj):
            has_marker = getattr(obj, cls.MARKER, None)
            if has_marker:
                return True
            closure = getattr(obj, '__closure__', None)
            c_func = None
            if closure:
                for c in closure:
                    contents = c.cell_contents
                    if inspect.ismethod(contents) or inspect.isfunction(contents):
                        c_func = contents
                        break
            if c_func and getattr(c_func, cls.MARKER, None):
                return True
        else:
            return False

    @classmethod
    def get_test_marker(cls, test_func_obj, key=None, default_value=None):

        test_marker = getattr(test_func_obj, cls.MARKER)
        if key and isinstance(key, str):
            return test_marker.get(key, default_value)
        else:
            return test_marker


testcase = Test
