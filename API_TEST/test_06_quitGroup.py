import unittest
import requests
import json
from pyBase import redis_im_handle, config_action
import time


# 依赖数据

# 数据使用dqy0401-dqy0500
ownerId = "dqy0401"
uid_list = [{"uid": "dqy0409"}, {"uid": "dqy0402"}, {"uid": "dqy0403"}, {"uid": "dqy0404", "alias": "del_member"},
            {"uid": "dqy0405"}, {"uid": "dqy0406"}, {"uid": "dqy0407"}, {"uid": "dqy0408"}]  # 建群

# 入参格式json
headers = {"Content-Type": "application/json"}  # 指定提交的是json

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标志定义
del_member_ok = False
msg_write_ok = False


class QuitGroup(unittest.TestCase):
    """退群"""

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

        """redis存储验证：td_group:g_id+gid 成功存贮：members、owner、createAt"""
        code_url = cls.url_common + cls.create_group
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"create_group",
            'uids': uid_list,
        }
        t = int(time.time())                                                # 请求前获取时间
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        assert r.json()["msg"] == "ok", r.json()['msg']
        cls.gid = r.json()["data"]["gid"]
        # # 校验时间戳
        # assert t <= int(redis_.hget_(gb+cls.gid, "createAt")) < t+10
        # 校验群主
        assert eval(redis_.hget_(gb+cls.gid, "owner")) == {"uid": ownerId, "alias": ""}, redis_.hget_(gb+cls.gid, "owner")
        # 校验群成员
        st = eval(redis_.hget_(gb+cls.gid, "members"))
        lu = uid_list + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]
        # 清空该群离线消息
        for uid_dict in eval(redis_.hget_(gb+cls.gid, "members"))+[{"uid": ownerId}]:
            redis_.hdel_all(tn+uid_dict['uid'])
            assert redis_.hgetall_(tn + uid_dict['uid']) == {}, '删除离线消息失败'

    def tearDown(self):
        print('>>>返回：', self.result)

    def test_01_quitGroup(self):
        """通过性验证：所有参数正常传入"""
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': uid_list[1]["uid"],
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print(">>>群成员list：", redis_.hget_(gb+self.gid, "members"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert uid_list[1] not in eval(redis_.hget_(gb+self.gid, "members")), [uid_list[1], uid_list, redis_.hget_(gb+self.gid, "members")]    # 校验该群员已经退群
        globals()["del_member_ok"] = True
        # 储存离线消息
        for uid_dict in uid_list+[{"uid": ownerId}]:
            if uid_dict["uid"] != uid_list[1]["uid"]:
                assert self.gid in json.dumps(redis_.hgetall_(tn + uid_dict["uid"])), [self.gid, uid_dict]  # 离线消息存储
        globals()["msg_write_ok"] = True

    def test_02_quitGroup(self):
        """redis存储验证：td_group:g_id+gid ：members，退群成功"""
        self.result = str(del_member_ok)
        self.assertTrue(del_member_ok, "退群失败")

    def test_03_quitGroup(self):
        """redis存储验证：删除人员后群发消息，该群用户离线，存储离线消息"""
        self.result = str(msg_write_ok)
        self.assertTrue(msg_write_ok, "离线消息发送失败")

    def test_04_quitGroup(self):
        """入参验证：uid字段缺失"""
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "uid不能为空", r.json()['msg']

    def test_05_quitGroup(self):
        """入参验证：gid字段缺失"""
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_06_quitGroup(self):
        """入参验证：uid入参为空'' """
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': '',
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "uid不能为空", r.json()['msg']

    def test_07_quitGroup(self):
        """入参验证：gid入参为空''"""
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': uid_list[1]["uid"],
            'gid': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_08_quitGroup(self):
        """业务逻辑：uid不属于本群"""
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': 'dqy0101',
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print('>>>当前群成员：', redis_.hget_(gb+self.gid, "members"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "non-members or owner does not degroup", r.json()['msg']

    def test_09_quitGroup(self):
        """业务逻辑：群主不能退群"""
        code_url = self.url_common + self.quit_group
        print('>>>请求地址：', code_url)
        code_data = {
            'uid': ownerId,
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "non-members or owner does not degroup", r.json()['msg']


if __name__ == "__main__":
    unittest.main()
