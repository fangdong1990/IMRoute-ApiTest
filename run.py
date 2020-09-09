# -*- coding:utf-8 -*-
import unittest
import os
import time
from HTMLTestRunner import HTMLTestRunner
from pyBase import config_action, send_email

api_re = config_action.ConfigAction("API.ini")
url_ = api_re.get("api_url", "local_url")  # 获取api的url地址


def allTests():
    """加载所有用例"""
    # path = './API_TEST'
    path = './API_TEST'
    # print(path)
    suit = unittest.defaultTestLoader.discover(path, pattern='test_*.py')
    return suit


def getNowTime():
    """获取当前时间"""
    return time.strftime('%Y-%m-%d %H_%M_%S')


def run(title_,is_sendEmail=0):
    fileName = os.path.join(r'./report', getNowTime()+title_+'_TestReport.html')
    fp = open(fileName, 'wb')
    runner = HTMLTestRunner(stream=fp, title=title_, description='域名：'+url_)
    runner.run(allTests())
    fp.close()
    f1 = open(fileName, 'r', encoding='utf-8')
    res = f1.read()
    fp.close()
    if is_sendEmail == 1:
        send_email.send_email(res, 'IM系统-API自动化测试')


if __name__ == '__main__':
    run("IM-API自动化测试报告", is_sendEmail=1)
