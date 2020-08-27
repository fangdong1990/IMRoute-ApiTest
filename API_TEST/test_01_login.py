import unittest
import requests
import json
from pyBase import config_action,get_md5
import time


class Login(unittest.TestCase):
    """登录接口：动态获取IM-URI"""
    @classmethod
    def setUpClass(cls):
        # 获取api地址数据
        api_re = config_action.ConfigAction("API.ini")
        cls.url_common = api_re.get("api_url", "local_url")          # 获取api的url地址
        cls.login_path = api_re.get("api_path", "login")              # 获取登录地址
        cls.create_group = api_re.get("api_path", "create_group")
        cls.add_member = api_re.get("api_path", "add_member")
        cls.del_group = api_re.get("api_path", "del_group")
        cls.del_member = api_re.get("api_path", "del_member")
        cls.quit_group = api_re.get("api_path", "quit_group")
        cls.change_owner = api_re.get("api_path", "change_owner")
        cls.get_group_info = api_re.get("api_path", "get_group_info")
        cls.send_msg = api_re.get("api_path", "send_msg")

        #  获取header_key数据
        cls.key = api_re.get("header_key", "key")

        # 登录接口数据
        cls.login_uid = "dqy0001"
        cls.login_alias = "dqy001_login"

    def tearDown(self):
        print('>>>返回：', self.result)

    def test_01_login(self):
        """通过性验证：uid、alias正常入参"""
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': self.login_alias,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']

    def test_02_login(self):
        """入参验证：alias字段缺失"""
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']

    def test_03_login(self):
        """入参验证：uid字段缺失"""
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'alias': self.login_alias,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "uid不能为空", r.json()['msg']

    def test_04_login(self):
        """入参验证：uid入参为空'' """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': '',
            'alias': self.login_alias,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "uid不能为空", r.json()['msg']

    def test_05_login(self):
        """入参验证：alias入参为空'' """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']

    def test_06_login(self):
        """header验证：uid参数缺失 """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "uid不能为空", r.json()['msg']

    def test_07_login(self):
        """header验证：timestamp参数缺失 """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "timestamp不能为空", r.json()['msg']

    def test_08_login(self):
        """header验证：sign参数缺失 """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "sign不能为空", r.json()['msg']

    def test_09_login(self):
        """header验证：Content-Type不为json """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid + timestamp_13 + self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "系统繁忙，请稍后再试", r.json()['msg']

    def test_A0_login(self):
        """header验证：uid入参为空'' """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": '',
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "uid不能为空", r.json()['msg']

    def test_A1_login(self):
        """header验证：timestamp入参为空'' """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": '',
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "timestamp不能为空", r.json()['msg']

    def test_A5_login(self):
        """header验证：sign入参为空'' """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": ''
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "sign不能为空", r.json()['msg']

    def test_A6_login(self):
        """header验证：sign无效 """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": 'ec84e7b9b45f0e8cd5710a471558b8d5'
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "签名校验失败", r.json()['msg']

    def test_A7_login(self):
        """header验证：data-uid与header-uid不一致 """
        code_url = self.url_common + self.login_path
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": self.login_uid,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(self.login_uid+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': 'dqy0025',
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']


if __name__ == "__main__":
    unittest.main()
