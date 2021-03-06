import unittest
import requests
import json
from pyBase import redis_im_handle, config_action, get_md5
import time


# 依赖数据

# 数据使用dqy0301-dqy0400
ownerId = "dqy0301"
uid_list = [{"uid": "dqy0309"}, {"uid": "dqy0302"}, {"uid": "dqy0303"}, {"uid": "dqy0304", "alias": "del_member"},{"uid": "dqy0305"},{"uid": "dqy0306"},{"uid": "dqy0307"},{"uid": "dqy0308"}]  # 建群

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标志定义
del_member_ok = False
msg_write_ok = False


class AelMember(unittest.TestCase):
    """删除群人员"""

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

        """redis存储验证：td_group:g_id+gid 成功存贮：members、owner、createAt"""
        code_url = cls.url_common + cls.create_group
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+cls.key)
                   }
        print(">>>请求头：", headers)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_delMember",
            'uids': uid_list,
            'msg_id': timestamp_13 + '_' + ownerId
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

    def test_01_delMember(self):
        """通过性验证：所有参数正常传入"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': [uid_list[1]],      # 删除dqy0302
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        print(">>>群成员list：",redis_.hget_(gb+self.gid, "members"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert redis_.hget_(gb+self.gid, "members") != "null", redis_.hget_(gb+self.gid, "members")
        assert uid_list[1] not in eval(redis_.hget_(gb+self.gid, "members")), [uid_list[1], uid_list, redis_.hget_(gb+self.gid, "members")]    # 校验该群员已经删除
        globals()["del_member_ok"] = True
        # 存储离线消息
        for uid_dict in uid_list+[{"uid": ownerId}]:
            if uid_dict != uid_list[1]:
                assert self.gid in json.dumps(redis_.hgetall_(tn + uid_dict["uid"])), [self.gid, uid_dict]  # 离线消息存储
        globals()["msg_write_ok"] = True

    def test_02_delMember(self):
        """redis存储验证：td_group:g_id+gid ：members，成功删除该成员"""
        self.result = str(del_member_ok)
        self.assertTrue(del_member_ok, "群成员删群人员失败")

    def test_03_delMember(self):
        """redis存储验证：删除人员后群发消息，该群用户离线，存储离线消息"""
        self.result = str(msg_write_ok)
        self.assertTrue(msg_write_ok, "离线消息发送失败")

    def test_04_delMember(self):
        """入参验证：ownerId字段缺失"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'gid': self.gid,
            'uids':  [uid_list[2]],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "onwerId不能为空", r.json()['msg']

    def test_05_delMember(self):
        """入参验证：gid字段缺失"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'uids':  [uid_list[2]],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_06_delMember(self):
        """入参验证：uids字段缺失"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "params null", r.json()['msg']

    def test_07_delMember(self):
        """入参验证：msg_id字段缺失"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids':  [uid_list[2]],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "msg_id不能为空", r.json()['msg']

    def test_08_delMember(self):
        """入参验证：msg_id字段未缺失"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids':  [uid_list[2]],
            'msg_id': ''
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "msg_id不能为空", r.json()['msg']

    def test_09_delMember(self):
        """入参验证：ownerId入参为空''"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': '',
            'gid': self.gid,
            'uids': [uid_list[2]],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "onwerId不能为空", r.json()['msg']

    def test_A0_delMember(self):
        """入参验证：gid入参为空''"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': '',
            'uids':  [uid_list[2]],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_A1_delMember(self):
        """入参验证：uids入参为空''"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': [],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "params null", r.json()['msg']

    def test_A2_delMember(self):
        """入参验证：gid无效''"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': '$12345678901234567890123456789011',
            'uids':  [uid_list[2]],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "not group owner", r.json()['msg']

    def test_A3_delMember(self):
        """业务逻辑验证：删除人员(单个)非本群人员"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        print('>>>群成员list：', redis_.hget_(gb+self.gid, "members"))
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': [{"uid": "dqy0101"}],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "non-members or owner cannot be deleted", r.json()['msg']
        assert [{"uid": "dqy0101"}] not in eval(redis_.hget_(gb + self.gid, "members")), [uid_list[1], uid_list,redis_.hget_(gb + self.gid,"members")]  # 校验该群员不存在

    def test_A4_delMember(self):
        """业务逻辑验证：删除人员(多个)为本群人员"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        print('>>>群成员：', eval(redis_.hget_(gb+self.gid, "members")))
        print('>>>删除人员列表：', uid_list[2:4])
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': uid_list[2:4],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        assert uid_list[2:4] not in eval(redis_.hget_(gb+self.gid, "members")), [uid_list[1], uid_list, redis_.hget_(gb+self.gid, "members")]    # 校验该群员已经删除

    def test_A5_delMember(self):
        """业务逻辑验证：删除人员(多个)中存在非本群人员"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': [{"uid": "dqy0305"}, {"uid": "dqy0102"}],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "non-members or owner cannot be deleted", r.json()['msg']

    def test_A6_delMember(self):
        """业务逻辑验证：非群主不可删除本群人员"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': uid_list[5]["uid"],
            'gid': self.gid,
            'uids': [uid_list[6]],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "not group owner", r.json()['msg']

    def test_A7_delMember(self):
        """业务逻辑验证：不可删除群主"""
        code_url = self.url_common + self.del_member
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'gid': self.gid,
            'uids': [{"uid": ownerId}],
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "non-members or owner cannot be deleted", r.json()['msg']


if __name__ == "__main__":
    unittest.main()