import unittest
import requests
import json
from pyBase import redis_im_handle,config_action
import time


# 依赖数据

# 数据使用dqy0501-dqy0600
ownerId = "dqy0501"
uid_list = [{"uid": "dqy0506"}, {"uid": "dqy0502"}, {"uid": "dqy0503"}, {"uid": "dqy0504"}, {"uid": "dqy0505", "alias": "change_owner"}]
add_uid = [{"uid": "dqy0510"}]

# 入参格式json
headers = {"Content-Type": "application/json"}  # 指定提交的是json

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标志定义
del_member_ok = False
msg_write_ok = False


class ChangeOwner(unittest.TestCase):
    """更换群主"""

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
            'name': ownerId+"change_owner",
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

    def test_01_changeOwner(self):
        """通过性验证：所有参数正常传入"""
        code_url = self.url_common + self.change_owner
        st_mem = eval(redis_.hget_(gb + self.gid, "members"))
        print('>>>更换群主前的群主信息', redis_.hget_(gb + self.gid, "owner"))
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            "targetOwnerId": uid_list[1]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print('>>>更换群主后的群主信息', redis_.hget_(gb + self.gid, "owner"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        # 校验群名
        assert redis_.hget_(gb+self.gid, "gName") == ownerId+"change_owner", [">>>>redis存储", eval(redis_.hget_(gb+self.gid, "gName")), ownerId+"change_owner"]
        # 校验群主，更换群主成功
        assert uid_list[1]['uid'] == eval(redis_.hget_(gb+self.gid, "owner"))['uid'], [uid_list[1], redis_.hget_(gb+self.gid, "owner")]
        globals()["del_member_ok"] = True
        # 存储离线消息,群成员+群主
        for uid_dict in uid_list+[{"uid": ownerId}]:
            assert self.gid in json.dumps(redis_.hgetall_(tn + uid_dict["uid"])), [self.gid, json.dumps(redis_.hgetall_(tn + uid_dict["uid"]))]  # 离线消息存储
        globals()["msg_write_ok"] = True
        # 校验群组成员
        lu = eval(redis_.hget_(gb + self.gid, "members"))
        lu.sort(key=lambda k: k.get("uid"))                                      # list排序
        st_mem.sort(key=lambda k: k.get("uid"))                                  # list排序
        assert lu == st_mem, ['>>>更换群主前的群成员信息', st_mem, '>>>更换群主后的群成员信息', lu]

    def test_02_changeOwner(self):
        """redis存储验证：td_group:g_id+gid ：owner，成功更换群主"""
        self.result = str(del_member_ok)
        self.assertTrue(del_member_ok, "更换群主失败")

    def test_03_changeOwner(self):
        """redis存储验证：更换群主后群发消息，该群用户离线，存储离线消息"""
        self.result = str(msg_write_ok)
        self.assertTrue(msg_write_ok, "离线消息发送失败")

    def test_04_changeOwner(self):
        """入参验证：ownerId字段缺失"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'gid': self.gid,
            "targetOwnerId": uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_05_changeOwner(self):
        """入参验证：gid字段缺失"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            "targetOwnerId": uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_06_changeOwner(self):
        """入参验证：targetOwnerId字段缺失"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "targetOwnerId不能为空", r.json()['msg']

    def test_07_changeOwner(self):
        """入参验证：ownerId入参为空''"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': '',
            'gid': self.gid,
            "targetOwnerId": uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_08_changeOwner(self):
        """入参验证：gid入参为空''"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            'gid': '',
            "targetOwnerId": uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_09_changeOwner(self):
        """入参验证：targetOwnerId入参为空''"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            'gid': self.gid,
            "targetOwnerId": "",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "targetOwnerId不能为空", r.json()['msg']

    def test_A0_changeOwner(self):
        """入参验证：ownerId非群主"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[3]["uid"],
            'gid': self.gid,
            "targetOwnerId": uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "Non-group manager", r.json()['msg']

    def test_A1_changeOwner(self):
        """入参验证：gid无效"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            'gid': "$12345678901234567890123456789011",
            "targetOwnerId": uid_list[2]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "Non-group manager", r.json()['msg']

    def test_A2_changeOwner(self):
        """入参验证：targetOwnerId非群成员"""
        code_url = self.url_common + self.change_owner
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            'gid': self.gid,
            "targetOwnerId": 'dqy0101',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == " non-member", r.json()['msg']

    def test_A3_changeOwner(self):
        """业务逻辑验证：更换的群主带备注"""
        code_url = self.url_common + self.change_owner
        st_owner = redis_.hget_(gb+self.gid, "owner")
        print(">>>更换群主前的onwer信息：", st_owner)
        print(">>>更换群主为：", uid_list[4])
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[1]["uid"],
            'gid': self.gid,
            "targetOwnerId": uid_list[4]["uid"],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print('>>>更换群主后的群主信息', redis_.hget_(gb + self.gid, "owner"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert eval(redis_.hget_(gb+self.gid, "owner"))['uid'] == uid_list[4]["uid"], "更换群主失败"
        assert eval(redis_.hget_(gb + self.gid, "owner")) == uid_list[4], "群主备注信息未跟新"

    def test_A4_changeOwner(self):
        """业务逻辑验证：更新群主成功后可添加人员"""
        code_url = self.url_common + self.add_member
        print(">>>群成员列表", redis_.hget_(gb+self.gid, "members"))
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[4]["uid"],
            'gid': self.gid,
            'uids': add_uid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert add_uid[0] in eval(redis_.hget_(gb+self.gid, "members")), redis_.hget_(gb+self.gid, "members")   # 验证添加成功

    def test_A5_changeOwner(self):
        """业务逻辑验证：更新群主成功后可删除人员"""
        code_url = self.url_common + self.del_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[4]["uid"],
            'gid': self.gid,
            'uids': add_uid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert add_uid not in eval(redis_.hget_(gb + self.gid, "members")), redis_.hget_(gb + self.gid, "members")  # 验证删除失败

    def test_A6_changeOwner(self):
        """业务逻辑验证：更新群主成功后可删除群"""
        code_url = self.url_common + self.del_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[4]["uid"],
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        # 验证删除群成功
        gid_key = gb+self.gid             # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        self.assertFalse(redis_.hexists_(gid_key, "members"), redis_.hexists_(gid_key, "members"))
        self.assertFalse(redis_.hexists_(gid_key, "owner"), "删除群信息失败")
        self.assertFalse(redis_.hexists_(gid_key, "createAt"), "删除群信息失败")


if __name__ == "__main__":
    unittest.main()