from models.user import User
import json
import redis


cache = redis.StrictRedis()


def cached_user_id(user_id):
    """
    根据user_id 返回 User对象。
    如果缓存命中，则从缓存中获取对象。
    如果缓存穿透，则从数据库查询，拿到数据后将数据序列化后存储到redis再返回。
    """
    key = 'user_id_{}'.format(user_id)
    try:
        # 拿到json 格式的数据
        v = cache[key]
    except KeyError:
        # 如果没有缓存
        user = User.one(id=user_id)
        v = json.dumps(user.json())
        cache.set(key, v)
        return user
    else:
        # json序列化为dict，dict生成User对象
        d = json.loads(v)
        user = User.get_model(d)
        return user
