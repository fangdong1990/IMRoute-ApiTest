from configparser import ConfigParser
import sys
from os.path import abspath, dirname
import os
import time


class ConfigAction:

    def __init__(self, file_name):
        """
        初始化操作，读取文件内容
        :param file_name:
        """
        self.cp = ConfigParser()
        if os.path.isabs(file_name): # 如果给到的路径是绝对路径
            # self.p = dirname(dirname(abspath(__file__)))
            # print(self.p)
            self.cp.read(file_name, encoding='utf-8')
            self.file_name = file_name
        else:
            self.p = dirname(dirname(abspath(__file__)))     # 获取项目文件的根目录
            sys.path.insert(0, self.p)                       # 将根目录地址暂存到系统环境path
            self.file_name = self.p + "\\" + file_name
            self.cp.read(self.file_name, encoding='utf-8')   # 根据文件地址读取内容

    def modify(self, sec, key_, val):
        """
        修改配置信息
        :param sec:
        :param opt:
        :param val:
        :return:
        """
        self.cp.set(sec, key_, val)            # 修改的区间，字段，值
        self.cp.write(open(self.file_name, "w", encoding='utf-8'))  # w方式，将原数据清除，重新写入
        se = self.cp.get(sec, key_)
        return se

    def get(self, section_, key_ = None):
        """
        获取配置信息
        :param section_:
        :return:
        """
        if key_ is None:
            se = self.cp.items(section_)
        else:
            se = self.cp.get(section_, key_)  # 根据section名字获取内容
        return se

    def remove_opt(self, section_, value):
        """
        根据值，删除对应的option
        :param section_:
        :param value:
        :return:
        """
        for item in self.cp.items(section_):
            if value in item:
                opt = list(item)[0]
                self.cp.remove_option(section_, opt)
                break
        else:
            return ('不存在'+value)
        self.cp.write(open(self.file_name, "w", encoding='utf-8'))  # w方式，将原数据清除，重新写入
        return '删除设备成功'

    def add_opt(self, section_, value):
        """
        根据值，添加对应的option
        :param section_:
        :param value:
        :return:
        """
        option = 'devices_'+str(int(time.time()))
        for item in self.cp.items(section_):
            if value not in item:
                self.cp.set(section_, option,value)
            else:
               return ('已存在'+value)
        self.cp.write(open(self.file_name, "w", encoding='utf-8'))  # w方式，将原数据清除，重新写入
        return '添加设备成功'


if __name__ == "__main__":
     cf= ConfigAction('API.ini')
     # v = cf.get('deviceID','deviceid')
     # print(v)
     # # a = cf.remove_opt('deviceID','ERRTT42')
     # # a = cf.add_opt('deviceID','ERRTT42')
     # global_path = ConfigAction('GLOBAL.ini').get('path_para','path_')
     # cp = ConfigAction(global_path)
     # a = cp.get('deviceID','deviceid')
     # c = cp.add_opt('deviceID','123')
     print(cf.get("api_url","local_url"))






