#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/03/30 15:49:32
'''
import io
import os
import sys
from appium import webdriver

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from WinAppUITest.utils.base_testcase import BaseTestCase
from WinAppUITest.utils.test_wrapper import testcase


class VNCViewerTest(BaseTestCase):
    """VNC Viewer 连接远程电脑桌面"""
    @classmethod
    def setUpClass(cls):
        desired_caps = {}
        desired_caps["app"] = r"C:\Users\cfgdc-pc 98\Desktop\vnc-4_1_2-x86_win32_viewer.exe"  # vnc viewer 的执行路径
        server_url = "http://127.0.0.1:4723"
        cls.driver = webdriver.Remote(server_url, desired_caps)

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, description='使用正确密码连接远程电脑桌面')
    def connect_remote_pc_desktop(self):

        ip = "10.201.15.253"
        pwd = "123456"
        self.sleep(5)  # 等待vnc viewer界面显示出来
        el_ok = self.driver.find_element_by_name("OK")
        el_ip = self.driver.find_element_by_accessibility_id('1001')  # 这个查找方法慎用，AutomationId 这个很有可能是动态值
        el_ip.clear()
        el_ip.send_keys(ip)
        el_ok.click()

        self.sleep(20)  # 上面点击ok后，到下一个界面显示出来需要时间，所以这里设置延时等待
        # for window_handle in self.driver.window_handles: #调试代码
            # self.driver.switch_to.window(window_handle)
            # print("self.driver.title=", self.driver.title)
            # print("self.driver.page_source=", self.driver.page_source)

        # 因为上面点击ok按钮后，界面消失后到弹出下一个界面后，需要切换到下一个界面的窗口，否则直接执行后续的代码会报错
        # 查找并切换到输入密码控件所在的窗口 代码 start -------
        vnc_title = "VNC Viewer : Authentication [No Encryption]"
        for window_handle in self.driver.window_handles:
            self.driver.switch_to.window(window_handle)
            if self.driver.title == vnc_title:
                break
        # 查找并切换到输入密码控件所在的窗口 代码 end   -------

        childrens = self.driver.find_elements_by_xpath("./*")  # 获取当前窗口下的所有子元素
        for c in childrens:
            # print("c.get_attribute("IsEnabled")=", c.get_attribute("IsEnabled"))
            if c.get_attribute("IsEnabled") == "true":  # 通过界面我们知道 只有输入密码框是可编辑的，所以使用该条件来判断是否密码输入框元素
                c.send_keys(pwd)
                break
        self.sleep(10)  # 这里延时是为了 显示输入密码的过程，否则就会执行下面的点击ok按钮，一闪而过
        self.driver.find_element_by_name("OK").click()

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.sleep(2)
        cls.driver.quit()


if __name__ == '__main__':
    VNCViewerTest.run_test()
