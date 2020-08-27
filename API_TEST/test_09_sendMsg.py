import unittest
import requests
import json
from pyBase import redis_im_handle, config_action,get_md5
import time


# 依赖数据

# 数据使用范围dqy0101-dqy0200
ownerId = "dqy0701"
uid_list = [{"uid": "dqy0705"}, {"uid": "dqy0702"}, {"uid": "dqy0703"}, {"uid": "dqy0704"},
{"uid": "dqy0706"}, {"uid": "dqy0707"}, {"uid": "dqy0708"}, {"uid": "dqy0709"}]

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标记定义
gid_action_ok = False
msg_write_ok = False


class SendMsg(unittest.TestCase):
    """发送消息"""

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

    def test_01_sendMsg(self):
        """通过性验证：所有参数正常传入group0、type1"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_01','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertTrue(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key存在
        assert 'is_text_type_01' in redis_.hget_(tn+uid_list[0]["uid"], str(timestamp13)), redis_.hget_(tn+uid_list[0]["uid"], str(timestamp13))     # 验证消息已储存

    def test_02_sendMsg(self):
        """入参验证：from_uid字段缺失"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_02','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "from_uid不能为空", r.json()['msg']

    def test_03_sendMsg(self):
        """入参验证：to_uid字段缺失"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_03','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "to_uid不能为空", r.json()['msg']

    def test_04_sendMsg(self):
        """入参验证：group字段缺失"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_04','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "group不能为空", r.json()['msg']

    def test_05_sendMsg(self):
        """入参验证：type字段缺失"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_05','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "type不能为空", r.json()['msg']

    def test_06_sendMsg(self):
        """入参验证：time字段缺失"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'data': "{'var1': 'is_text_type_06','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "time不能为空", r.json()['msg']

    def test_07_sendMsg(self):
        """入参验证：data字段缺失"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "data不能为空", r.json()['msg']

    def test_08_sendMsg(self):
        """入参验证：from_uid入参空'' """
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': '',
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_07','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "from_uid不能为空", r.json()['msg']

    def test_09_sendMsg(self):
        """入参验证：to_uid入参空'' """
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': '',
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_08','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "to_uid不能为空", r.json()['msg']

    def test_A0_sendMsg(self):
        """入参验证：group入参空'' """
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': '',              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_09','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "group只能是0或1", r.json()['msg']

    def test_A1_sendMsg(self):
        """入参验证：type入参空'' """
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': '',               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_text_type_10','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "type不能为空", r.json()['msg']

    def test_A2_sendMsg(self):
        """入参验证：time入参空'' """
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': '',
            'data': "{'var1': 'is_text_type_11','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "time不能为空", r.json()['msg']

    def test_A3_sendMsg(self):
        """入参验证：data入参空'' """
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': ''
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "data不能为空", r.json()['msg']

    def test_A4_sendMsg(self):
        """业务逻辑： type0：发送cmd消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 0,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            'data': "{'var1': 'is_cmd_type_01','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertFalse(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key不存在

    def test_A5_sendMsg(self):
        """业务逻辑： type2：发送image消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 2,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{  \"var2\" : \"c2flL7IT8+RgyxzE4RxVc8nfGKFb5bcpjvavfXBt70jTk7wkPAUJi8fIQ9pu\\\/5ofyAw57gT93h\\\/2UaYokfjNug==\",  \"var5\" : \"\",  \"var3\" : \"image.jpeg\",  \"var1\" : \"c2flL7IT8+RgyxzE4RxVcxvt65d5fsKmAg8+VDZXLcuRYaK2NFem26iYDJZJrNMoyAw57gT93h\\\/2UaYokfjNug==\",  \"var4\" : \"\"}",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertTrue(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key存在

    def test_A6_sendMsg(self):
        """业务逻辑： type3：发送audio消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 3,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{  \"var2\" : \"1\",  \"var5\" : \"\",  \"var3\" : \"\",  \"var1\" : \"c2flL7IT8+RgyxzE4RxVc5lFM64IEXIfcgFYBA2WARLMeECeiuUW5hHLb09y5i\\\/hbvW\\\/U4zF+BaVmk\\\/g5mD09A==\",  \"var4\" : \"\"}",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertTrue(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key存在

    def test_A7_sendMsg(self):
        """业务逻辑： type4：发送video消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 4,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{  \"var2\" : \"c2flL7IT8+RgyxzE4RxVc6VjdXcWTBE02Nf1F0MRJB3NN4eSPsOZBBvnVZQ\\\/RTBpyAw57gT93h\\\/2UaYokfjNug==\",  \"var5\" : \"\",  \"var3\" : \"video.mp4.mp4\",  \"var1\" : \"c2flL7IT8+RgyxzE4RxVc38GRp2fepoHtiV9wJEfq6AW2kDB0RPMD1N9aMzE9T7aKPOu608vpr73\\\/IDiN6AuGw==\",  \"var4\" : \"0\"}",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertTrue(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key存在

    def test_A8_sendMsg(self):
        """业务逻辑： type5：发送file消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 5,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{  \"var2\" : \"c2flL7IT8+RgyxzE4RxVc6VjdXcWTBE02Nf1F0MRJB3NN4eSPsOZBBvnVZQ\\\/RTBpyAw57gT93h\\\/2UaYokfjNug==\",  \"var5\" : \"\",  \"var3\" : \"video.mp4.mp4\",  \"var1\" : \"c2flL7IT8+RgyxzE4RxVc38GRp2fepoHtiV9wJEfq6AW2kDB0RPMD1N9aMzE9T7aKPOu608vpr73\\\/IDiN6AuGw==\",  \"var4\" : \"0\"}",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertTrue(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key存在

    def test_A9_sendMsg(self):
        """业务逻辑： type6：发送position消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 6,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{  \"var2\" : \"120.3863338595745\",  \"var5\" : \"\",  \"var3\" : \"永康路3号\",  \"var1\" : \"36.1739649370593\",  \"var4\" : \"\"}",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        self.assertTrue(redis_.hexists_(tn+uid_list[0]["uid"], str(timestamp13)), timestamp13)     # 判断key存在
        # assert '永康路3号' in redis_.hget_(tn+uid_list[0]["uid"], str(timestamp13)), redis_.hget_(tn+uid_list[0]["uid"], str(timestamp13))     # 验证消息已储存

    def test_B0_sendMsg(self):
        """业务逻辑： type100：无效"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': uid_list[0]["uid"],
            'group': 0,              # 0-单聊，1-群聊
            'type': 100,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{  \"var2\" : \"120.3863338595745\",  \"var5\" : \"\",  \"var3\" : \"永康路3号\",  \"var1\" : \"36.1739649370593\",  \"var4\" : \"\"}",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "type只能是0至15之间的整数", r.json()['msg']

    def test_B1_sendMsg(self):
        """业务逻辑：发送群消息"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': ownerId,
            'to_uid': self.gid,
            'group': 1,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{'var1': 'is_test_type_group','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']

    def test_B2_sendMsg(self):
        """业务逻辑：from_uid非群成员"""
        code_url = self.url_common + self.send_msg
        timestamp_13 = str(int(time.time()*1000))
        headers = {
            "Content-Type": "application/json",
            "uid": ownerId,
            "timestamp": timestamp_13,
            "sign": get_md5.get_md5_value(ownerId+timestamp_13+self.key)
                   }
        print(">>>请求头：", headers)
        print(">>>群成员："+redis_.hget_(gb+self.gid, "members"))
        print('>>>请求地址：', code_url)
        timestamp13 = int(time.time()*1000)
        code_data = {
            'from_uid': "dqy0002",
            'to_uid': self.gid,
            'group': 1,              # 0-单聊，1-群聊
            'type': 1,               # 0-cmd，1-text，2-image，3-audio，4-video，5-file，6-position
            'time': timestamp13,
            "data": "{'var1': 'is_test_type_group','var2': '','var3': '','var4': '','var5': ''}"
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "from_uid is not in group", r.json()['msg']


if __name__ == "__main__":
    unittest.main()












