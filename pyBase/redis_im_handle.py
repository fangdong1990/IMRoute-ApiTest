import redis
from pyBase import config_action

redis_im = config_action.ConfigAction("DB.ini")
host_ = redis_im.get("redis_IM", "host")
port_ = redis_im.get("redis_IM", "port")
db_ = redis_im.get("redis_IM", "db")


class RedisIm:

    def __init__(self):
        self.db_con = redis.Redis(host=host_, port=port_, db=db_, decode_responses=True)   # redis 取出的结果默认是字节，我们可以设定 decode_responses=True 改成字符串

    """
    ===========================redis string操作==============================
    即一个key对应一个string值
    """
    def get_(self, key_):
        """获取值 value为字符串类型"""
        return self.db_con.get(key_)

    def set_(self, key_, value_):
        """添加新值"""
        self.db_con.set(key_, value_)

    def delete_(self, key_):
        """删除值"""
        self.db_con.delete(key_)

    def exists_(self, key_):
        """判断key是否存在"""
        self.db_con.exists(key_)

    """
    =============================redis hash操作============================
    即一个key对应一个字典
    """
    def hget_(self, key_,hash_key_):
        """获取key_对应的hash中获取根据key获取value"""
        return self.db_con.hget(key_, hash_key_)

    def hgetall_(self, key_):
        """获取key_对应hash的所有键值"""
        return self.db_con.hgetall(key_)

    def hlen_(self, key_):
        """获取key_对应的hash中键值对的个数"""
        return self.db_con.hlen(key_)

    def hkeys_(self, key_):
        """获取key_对应的hash中所有的key的值"""
        return self.db_con.hkeys(key_)

    def hvals_(self, key_):
        """获取key_对应的hash中所有的value的值"""
        return self.db_con.hvals(key_)

    def hdel_(self, key_,hash_key_):
        """删除key_对应的hash中指定key的键值对"""
        self.db_con.hdel(key_, hash_key_)

    def hdel_all(self, key_):
        """删除key_对应所以键值对，以及该key_"""
        hash_key_list = self.hkeys_(key_)
        for hash_key in hash_key_list:
            self.hdel_(key_, hash_key)

    def hexists_(self, key_, hash_key_):
        """检查key_对应的hash是否存在当前传入的hash_key_"""
        return self.db_con.hexists(key_, hash_key_)


if __name__ == "__main__":
    a = RedisIm()
    # a.set_('foo1', 'bar')
    # print(a.hgetall_("td_group:g_id:$0a2926a4d6fd11eabf75b42e9910caab"))
    # b = a.hkeys_("td_group:g_id:$0a2926a4d6fd11eabf75b42e9910caab")
    # c = a.hlen_("td_group:g_id:$0a2926a4d6fd11eabf75b42e9910caab")
    # print(b)
    # print(c)
    # a.hdel_all("td_nlm_t:zhang1")

    # b = a.hgetall_("td_nlm_t:dqy0007")
    # print(b)
    # c = a.hget_("td_nlm_t:dqy0705","1597635423126")
    c = a.hexists_("td_nlm_t:dqy0705","1597635423126")
    print(c)
    # a.set_('foo', 'bar')

