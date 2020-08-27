import unittest
import requests
import json
from pyBase import redis_im_handle, config_action,get_md5
import time


# 依赖数据
ownerId = "dqy0601"
uid_list = [{"uid": "dqy0606"}, {"uid": "dqy0602"}, {"uid": "dqy0603"}, {"uid": "dqy0604"}, {"uid": "dqy0605", "alias": "createGroup_GetGroupInfo"}]

# redis相关
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象


class GetGroupInfo(unittest.TestCase):
    """获取群信息"""

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

        """建群成功后获取gid"""
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
            'name': ownerId+"_GetGroupInfo",
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

    def test_01_getGroupInfo(self):
        """通过性验证：所有参数正常传入"""
        code_url = self.url_common + self.get_group_info
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
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']

    def test_02_getGroupInfo(self):
        """入参验证：gid字段缺失"""
        code_url = self.url_common + self.get_group_info
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
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert "gid不能为空" in r.json()["msg"], r.json()['msg']

    def test_03_getGroupInfo(self):
        """入参验证：gid入参为空'' """
        code_url = self.url_common + self.get_group_info
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
            'gid': '',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert "gid不能为空" in r.json()["msg"], r.json()['msg']

    def test_04_getGroupInfo(self):
        """入参验证：gid无效"""
        code_url = self.url_common + self.get_group_info
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
            'gid': '165656664155',
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert "165656664155" in r.json()["msg"], r.json()['msg']
        assert "not exists" in r.json()["msg"], r.json()['msg']


if __name__ == "__main__":
    unittest.main()
