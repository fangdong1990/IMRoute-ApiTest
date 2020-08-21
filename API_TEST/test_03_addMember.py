import unittest
import requests
import json
from pyBase import redis_im_handle, config_action
import time


# 依赖数据

# 数据使用范围dqy0101-dqy0200
ownerId = "dqy0101"
uid_list = [{"uid": "dqy0105"}, {"uid": "dqy0102"}, {"uid": "dqy0103"}, {"uid": "dqy0104"}]
add_uids1 = [{"uid": "dqy0106"}]
add_uids3 = [{"uid": "dqy0109"}, {"uid": "dqy0107"}, {"uid": "dqy0108", "alias": "add_member"}]
add_uids4 = [{"uid": "dqy0102"}, {"uid": "dqy0110"}, {"uid": "dqy0111", "alias": "add_member"}]


# 入参格式json
headers = {"Content-Type": "application/json"}  # 指定提交的是json

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标记定义
gid_action_ok = False
msg_write_ok = False


class AddMember(unittest.TestCase):
    """添加群成员"""

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
            'name': ownerId+"_AddMember",
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

    def test_01_addMember(self):
        """通过性验证：正常入参：ownerId、gid、uids"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': add_uids1,
        }
        print(">>>>添加新成员前的群员列表", redis_.hget_(gb+self.gid, "members"))
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        print(">>>>添加新成员后的群员列表", redis_.hget_(gb+self.gid, "members"))
        # 添加新成员后，群标识的用户列表 需要添加新用户
        assert redis_.hget_(gb+self.gid, "members") != "null", redis_.hget_(gb+self.gid, "members")
        assert add_uids1[0] in eval(redis_.hget_(gb+self.gid, "members")), [add_uids1, redis_.hget_(gb+self.gid, "members")]
        globals()["gid_action_ok"] = True
        # 校验离线消息
        assert {"uid": ownerId}in eval(redis_.hget_(gb+self.gid, "members")),[{"uid": ownerId},eval(redis_.hget_(gb+self.gid, "members"))]
        for uid_dict in eval(redis_.hget_(gb+self.gid, "members")):
            assert self.gid in json.dumps(redis_.hgetall_(tn + uid_dict["uid"])), [self.gid, json.dumps(redis_.hgetall_(tn + uid_dict["uid"]))]
        globals()["msg_write_ok"] = True

    def test_02_addMember(self):
        """redis存储验证：td_group:g_id+gid 成功存贮：members"""
        self.result = str(gid_action_ok)
        self.assertTrue(gid_action_ok, "添加人员失败")

    def test_03_addMember(self):
        """redis存储验证：添加成功群发消息，账号全部离线：离线消息存储''"""
        self.result = str(msg_write_ok)
        self.assertTrue(msg_write_ok, "离线消息发送失败")

    def test_04_addMember(self):
        """业务逻辑验证：一次添加多人，部分用户携带alias字段"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': add_uids3,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert redis_.hget_(gb+self.gid, "members") != "null", redis_.hget_(gb+self.gid, "members")
        for uid_dict in add_uids3:
            assert uid_dict in eval(redis_.hget_(gb+self.gid, "members")), [add_uids3, redis_.hget_(gb+self.gid, "members")]          # 添加新成员后，群标识的用户列表 需要添加新用户

    def test_05_addMember(self):
        """业务逻辑验证：即将添加人员在当前群全部已存在"""
        code_url = self.url_common + self.add_member
        st_uids =eval(redis_.hget_(gb + self.gid, "members"))
        print(">>>初始群成员：", st_uids)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': add_uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print(">>>添加成员后群成员：", eval(redis_.hget_(gb + self.gid, "members")))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "Member already exists", r.json()['msg']
        assert eval(redis_.hget_(gb + self.gid, "members")) == st_uids    # 验证群成员为添加

    def test_06_addMember(self):
        """业务逻辑验证：即将添加人员在当前群部分已存在"""
        code_url = self.url_common + self.add_member
        st_uids =eval(redis_.hget_(gb + self.gid, "members"))
        print(">>>初始群成员：", st_uids)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': add_uids4,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print(">>>添加成员后群成员：", eval(redis_.hget_(gb + self.gid, "members")))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "Member already exists", r.json()['msg']
        assert eval(redis_.hget_(gb + self.gid, "members")) == st_uids     # 验证群成员为添加

    def test_07_addMember(self):
        """入参验证：ownerId字段缺失"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'gid': self.gid,
            'uids': add_uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_08_addMember(self):
        """入参验证：gid字段缺失"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'uids': add_uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_09_addMember(self):
        """入参验证：uids字段缺失"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "params err", r.json()['msg']

    def test_A0_addMember(self):
        """入参验证：ownerId入参为空''"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': '',
            'gid': self.gid,
            'uids': add_uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_A1_addMember(self):
        """入参验证：gid入参为空''"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': '',
            'uids': add_uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_A2_addMember(self):
        """入参验证：uids入参为空[] """
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': [],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "params err", r.json()['msg']

    def test_A3_addMember(self):
        """入参验证：gid无效''"""
        code_url = self.url_common + self.add_member
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': '$12345678901234567890123456789011',
            'uids': add_uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert '$12345678901234567890123456789011' in r.json()["msg"], r.json()['msg']
        assert 'not exists' in r.json()["msg"], r.json()['msg']


if __name__ == "__main__":
    unittest.main()