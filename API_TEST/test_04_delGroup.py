import unittest
import requests
import json
from pyBase import redis_im_handle, config_action, get_md5
import time


# 依赖数据

# 数据使用dqy0201-dqy0300
ownerId = "dqy0201"
uid_list = [{"uid": "dqy0205"}, {"uid": "dqy0202"}, {"uid": "dqy0203"}, {"uid": "dqy0204"}]

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标志定义
gid_del_ok = False
msg_write_ok = False


class DelGroup(unittest.TestCase):
    """删除群"""

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
            'name': ownerId+"delGroup",
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

    def test_01_delGroup(self):
        """通过性验证：入参正常：ownerId、gid"""
        code_url = self.url_common + self.del_group
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
        assert r.json()["msg"] == "ok", r.json()['msg']

        # 验证群标识和数据删除成功
        gid_key = gb+self.gid             # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        self.assertFalse(redis_.hexists_(gid_key, "members"), redis_.hexists_(gid_key, "members"))
        self.assertFalse(redis_.hexists_(gid_key, "owner"), "删除群主失败")
        self.assertFalse(redis_.hexists_(gid_key, "createAt"), "删除群信息的时间戳失败")
        globals()["gid_del_ok"] = True

        # 验证删群后，离线消息全部储存
        for uid_dict in uid_list+[{"uid": ownerId}]:
            assert self.gid in json.dumps(redis_.hgetall_(tn + uid_dict["uid"])), [self.gid, json.dumps(redis_.hgetall_(tn + uid_dict["uid"]))]  # 离线消息存储
        globals()["msg_write_ok"] = True

    def test_02_delGroup(self):
        """redis存储验证：td_group:g_id+gid 群标识和群信息删除成功"""
        self.result = str(gid_del_ok)
        self.assertTrue(gid_del_ok, '群数据删除失败')

    def test_03_delGroup(self):
        """redis存储验证：删除群后群发消息，该群用户离线，存储离线消息"""
        self.result = str(msg_write_ok)
        self.assertTrue(msg_write_ok, "离线消息发送失败")

    def test_04_delGroup(self):
        """入参验证：ownerId字段缺失"""
        code_url = self.url_common + self.del_group
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
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_05_delGroup(self):
        """入参验证：gid字段缺失"""
        code_url = self.url_common + self.del_group
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
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_06_delGroup(self):
        """入参验证：msg_id字段缺失"""
        code_url = self.url_common + self.del_group
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
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "msg_id不能为空", r.json()['msg']

    def test_07_delGroup(self):
        """入参验证：msg_id字段为空"""
        code_url = self.url_common + self.del_group
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
            'msg_id': ''
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "msg_id不能为空", r.json()['msg']

    def test_08_delGroup(self):
        """入参验证：ownerId入参为空''"""
        code_url = self.url_common + self.del_group
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
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_09_delGroup(self):
        """入参验证：gid入参为空''"""
        code_url = self.url_common + self.del_group
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
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid不能为空", r.json()['msg']

    def test_A0_delGroup(self):
        """入参验证：gid无效"""
        code_url = self.url_common + self.del_group
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
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid or ownerId  is err", r.json()['msg']

    def test_A1_delGroup(self):
        """入参验证：ownerId无效"""
        code_url = self.url_common + self.del_group
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
            'ownerId': 'dqywjfksf',
            'gid': self.gid,
            'msg_id': timestamp_13 + '_' + ownerId
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "gid or ownerId  is err", r.json()['msg']


if __name__ == "__main__":
    unittest.main()
