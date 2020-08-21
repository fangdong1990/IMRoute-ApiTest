import unittest
import requests
import json
from pyBase import config_action

headers = {"Content-Type": "application/json"}  # 指定提交的是json


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

        # 获取用户登录数据
        para = config_action.ConfigAction("PARAMETER.ini")

        # 登录接口数据
        cls.login_uid = para.get("login_userdata", "uid")
        cls.login_alias = para.get("login_userdata", "alias")

    def tearDown(self):
        print('>>>返回：', self.result)

    def test_01_login(self):
        """通过性验证：uid、alias正常入参"""
        code_url = self.url_common + self.login_path
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
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': self.login_uid,
            'alias': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']


if __name__ == "__main__":
    unittest.main()
