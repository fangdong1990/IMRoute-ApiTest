# -*- coding: utf-8 -*-

"""
Author:dongqiyun
Email:1808503589@qq.com

date:2020/8/27 9:12
"""
import hashlib


def get_md5_value(str):
    my_md5 = hashlib.md5()               # 获取一个MD5的加密算法对象
    my_md5.update(str.encode('utf-8'))   # 得到MD5消息摘要
    my_md5_Digest = my_md5.hexdigest()   # 以16进制返回消息摘要，32位
    return my_md5_Digest


if __name__ == "__main__":
    a=get_md5_value("dsjfisjdkokdogkog")
    print(a)