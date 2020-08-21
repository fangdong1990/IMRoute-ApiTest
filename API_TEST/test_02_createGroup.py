import unittest
import requests
import json
from pyBase import redis_im_handle,config_action
import time

# 依赖数据

# 使用数据范围dqy0001-dqy0100
# 建群数据默认不含群主
ownerId = "dqy0001"
uids_alias_all = [{"uid": "dqy0005", "alias": "dqy0005_CreateGroup"}, {"uid": "dqy0002","alias": "dqy0002_CreateGroup"},{"uid": "dqy0003","alias": "dqy0003_CreateGroup"}, {"uid": "dqy0004","alias": "dqy0004_CreateGroup"}]
uids_alias_part = [{"uid": "dqy0005", "alias": "dqy0005_CreateGroup"}, {"uid": "dqy0002"}, {"uid": "dqy0003"}, {"uid": "dqy0004","alias": "dqy0004_CreateGroup"}]
uids4 = [{"uid": "dqy0005"}, {"uid": "dqy0002"}, {"uid": "dqy0003"}, {"uid": "dqy0004"}]
uids3 = [{"uid": "dqy0005"}, {"uid": "dqy0002"}, {"uid": "dqy0003"}]
uids2 = [{"uid": "dqy0005"}, {"uid": "dqy0002"}]
uids5 = [{"uid": "dqy0005"}, {"uid": "dqy0002"}, {"uid": "dqy0002"}]
uids1 = [{"uid": "dqy0005"}]
uids6 = [{"uid": "dqy0002"}, {"uid": "dqy0002"}]
uids_ownerId = [{"uid": "dqy0001"}, {"uid": "dqy0002"}, {"uid": "dqy0003"}]
uids7 = [{"uid": "dqy0001"}, {"uid": "dqy0002"}]
uids_lots = [{"uid": "dqy0005"}, {"uid": "dqy0007"}, {"uid": "dqy0043"}, {"uid": "dqy0014"}, {"uid": "dqy0067"},
             {"uid": "dqy0027"}, {"uid": "dqy0079"}, {"uid": "dqy0013"}, {"uid": "dqy0066"}, {"uid": "dqy0072"},
             {"uid": "dqy0018"}, {"uid": "dqy0030"}, {"uid": "dqy0004"}, {"uid": "dqy0076"}, {"uid": "dqy0020"},
             {"uid": "dqy0059"}, {"uid": "dqy0021"}, {"uid": "dqy0045"}, {"uid": "dqy0016"}, {"uid": "dqy0074"},
             {"uid": "dqy0087"}, {"uid": "dqy0042"}, {"uid": "dqy0100"}, {"uid": "dqy0057"}, {"uid": "dqy0041"},
             {"uid": "dqy0082"}, {"uid": "dqy0009"}, {"uid": "dqy0028"}, {"uid": "dqy0015"}, {"uid": "dqy0019"},
             {"uid": "dqy0023"}, {"uid": "dqy0029"}, {"uid": "dqy0070"}, {"uid": "dqy0061"}, {"uid": "dqy0071"},
             {"uid": "dqy0086"}, {"uid": "dqy0069"}, {"uid": "dqy0094"}, {"uid": "dqy0051"}, {"uid": "dqy0083"},
             {"uid": "dqy0024"}, {"uid": "dqy0084"}, {"uid": "dqy0010"}, {"uid": "dqy0031"}, {"uid": "dqy0011"},
             {"uid": "dqy0098"}, {"uid": "dqy0003"}, {"uid": "dqy0054"}, {"uid": "dqy0093"}, {"uid": "dqy0056"},
             {"uid": "dqy0096"}, {"uid": "dqy0060"}, {"uid": "dqy0058"}, {"uid": "dqy0095"}, {"uid": "dqy0085"},
             {"uid": "dqy0075"}, {"uid": "dqy0091"}, {"uid": "dqy0036"}, {"uid": "dqy0092"}, {"uid": "dqy0055"},
             {"uid": "dqy0202"}]

# 入参格式json
headers = {"Content-Type": "application/json"}  # 指定提交的是json

# redis数据存贮
gb = "td_group:g_id:"                  # 群标识
tn = "td_nlm_t:"                       # 离线标识
redis_ = redis_im_handle.RedisIm()     # 实例化redis操作对象

# 标记定义
gid_action_ok = False
msg_write_ok = False


class CreateGroup(unittest.TestCase):
    """建群"""

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

    def tearDown(self):
        print('>>>返回：', self.result)

    def test_01_createGroup(self):
        """通过性验证：ownerId name uids正常入参"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids4,
        }
        t = int(time.time())
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_ = r.json()["data"]["gid"]
        assert t <= int(redis_.hget_(gb+gid_, "createAt")),[t, int(redis_.hget_(gb+gid_, "createAt"))]          # 校验时间戳为当前时间
        assert eval(redis_.hget_(gb+gid_, "owner")) == {"uid": ownerId, "alias": ""}, redis_.hget_(gb+gid_, "owner")
        self.assertEqual(redis_.hget_(gb+gid_, "gName"), ownerId+"_CreateGroup", redis_.hget_(gb+gid_, "gName"))
        # 校验群成员
        st = eval(redis_.hget_(gb+gid_, "members"))
        lu = uids4 + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]
        globals()["gid_action_ok"] = True  # 建群数据都写入成功

        # 建群成功后返回的gid值唯一且第一次出现，故通过校验离线消息的gid值即可校验是否存储离线消息
        for uid_dict in uids4+[{"uid": ownerId}]:
            assert gid_ in json.dumps(redis_.hgetall_(tn + uid_dict["uid"])), [gid_, json.dumps(redis_.hgetall_(tn + uid_dict["uid"]))]
        globals()["msg_write_ok"] = True

    def test_02_createGroup(self):
        """redis存储验证：td_group:g_id+gid：members==uids、owner==ownerId、createAt==当前时间"""
        self.result = str(gid_action_ok)
        self.assertTrue(gid_action_ok, "建群失败")

    def test_03_createGroup(self):
        """redis存储验证：td_nlm_t:+uid :建群成功群发消息，目前账号全部离线：离线消息存储"""
        self.result = str(msg_write_ok)
        self.assertTrue(msg_write_ok, "离线消息发送失败")

    def test_04_createGroup(self):
        """入参验证：ownerId字段缺失"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'name': ownerId+"_CreateGroup",
            'uids': uids4,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_05_createGroup(self):
        """入参验证：name字段缺失:目前约定字段必填"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'uids': uids4,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "params err", r.json()['msg']

    def test_06_createGroup(self):
        """入参验证：uids字段缺失"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId + "_CreateGroup",
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "no arr", r.json()['msg']

    def test_07_createGroup(self):
        """入参验证：ownerId入参为空'' """
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': '',
            'name': ownerId+"_CreateGroup",
            'uids': uids4,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ownerId不能为空", r.json()['msg']

    def test_08_createGroup(self):
        """入参验证：name入参为空'' """
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': '',
            'uids': uids4,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_key = gb+r.json()["data"]["gid"]                 # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids4 + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_09_createGroup(self):
        """入参验证：uids入参为空[] """
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': [],
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "members number err", r.json()['msg']

    def test_A0_createGroup(self):
        """入参验证：uids入参部分含alias"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids_alias_part,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_key = gb+r.json()["data"]["gid"]                 # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids_alias_part + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A1_createGroup(self):
        """入参验证：uids入参全部含alias"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids_alias_all,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_key = gb+r.json()["data"]["gid"]                 # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids_alias_all + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A2_createGroup(self):
        """业务逻辑验证：添加群成员uids为1 """
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids1,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "members number err", r.json()['msg']

    def test_A3_createGroup(self):
        """业务逻辑验证：添加群成员uids为2 """
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids2,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_key = gb+r.json()["data"]["gid"]                 # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids2 + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A4_createGroup(self):
        """业务逻辑验证：添加群成员uids为3"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids3,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_key = gb+r.json()["data"]["gid"]                 # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids3 + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A5_createGroup(self):
        """业务逻辑验证：添加群人员uids为lots(61)"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids_lots,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        gid_key = gb+r.json()["data"]["gid"]                 # 获取td_group:g_id:$1050af38d7bc11eaa53eb42e9910caab
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids_lots + [{"uid": ownerId}]
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A6_createGroup(self):
        """业务逻辑验证：建群uids(3)含ownerId-可建群成功"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids_ownerId,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        gid_key = gb+r.json()["data"]["gid"]
        print('>>>请求参数：', json.dumps(code_data))
        print(">>>建群完成后的群员list：", redis_.hget_(gid_key, "members"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        # 校验群成员
        st = eval(redis_.hget_(gid_key, "members"))
        lu = uids_ownerId
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A7_createGroup(self):
        """业务逻辑验证：建群uids(3)中含重复成员2-去除重复人员后建群"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids5,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        gid_key = gb + r.json()["data"]["gid"]
        print('>>>请求参数：', json.dumps(code_data))
        print(">>>建群完成后的群员list：", redis_.hget_(gid_key, "members"))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "ok", r.json()['msg']
        st = eval(redis_.hget_(gid_key, "members"))
        lu = [{"uid": "dqy0005"}, {"uid": "dqy0002"}]+[{"uid": ownerId}]  # 建群时自动去重
        st.sort(key=lambda k: k.get("uid"))   # list排序
        lu.sort(key=lambda k: k.get("uid"))   # list排序
        assert st == lu, [st, lu]

    def test_A8_createGroup(self):
        """业务逻辑验证：建群uids(2)中含重复成员2"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids6,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "members number err", r.json()['msg']

    def test_A9_createGroup(self):
        """业务逻辑验证：建群uids(2)含ownerId"""
        code_url = self.url_common + self.create_group
        print('>>>请求地址：', code_url)
        code_data = {
            'ownerId': ownerId,
            'name': ownerId+"_CreateGroup",
            'uids': uids7,
        }
        r = requests.post(url=code_url, data=json.dumps(code_data), headers=headers)
        print('>>>请求参数：', json.dumps(code_data))
        self.result = json.dumps(r.json(), sort_keys=True, indent=4, ensure_ascii=False)
        assert r.json()["msg"] == "members number err", r.json()['msg']


if __name__ == "__main__":
    unittest.main()
