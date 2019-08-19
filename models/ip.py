from json import JSONDecodeError
from models.base_model import SQLMixin, db
import requests
from pyquery import PyQuery as pq
import time
import json


def format_time():
    f = '%Y-%m-%d %H:%M:%S'
    unix_timestamp = time.time()
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def save(data, path):
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(s)


def load(path):
    with open(path, 'r', encoding='UTF-8') as f:
        try:
            s = json.loads(f.read())
        except JSONDecodeError:
            s = f.read()
        else:
            pass
        return s


class Ip(object):
    def __init__(self, form):
        self.locate = form.get('locate', '')
        self.logintime = form.get('logintime', '')

    @classmethod
    def db_path(cls):
        databasename = cls.__name__
        path = 'data/{}.txt'.format(databasename)
        return path

    @classmethod
    def all(cls):
        path = cls.db_path()
        models = load(path)
        ms = [cls(m) for m in models]
        return ms

    def save(self):
        models = self.all()
        models.append(self)
        models.sort(key=lambda models: models.logintime, reverse=True)
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)


def ip_from_url(url):
    r = requests.get(url)
    page = r.content
    p = page.decode('utf-8')
    print(p)
    e = pq(page)
    locate = e('.c-span21.c-span-last.op-ip-detail').text()
    logintime = format_time()
    form = dict(
        locate=locate,
        logintime=logintime,
    )
    m = Ip(form)
    return m


def get_ip(ip):
    url = 'http://www.baidu.com/s?wd={}&rsv_spt=1&rsv_iqid=0xcc7349fc00015788&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=1&rsv_dl=tb&oq=IP%25E5%259C%25B0%25E5%259D%2580%25E6%259F%25A5%25E8%25AF%25A2&inputT=669&rsv_t=cb3dCM1bKoYex379NF0T4nzab4RB2wYS%2BDSnvkGeFGUcN%2BArCu0gddrDSHePl%2BsjXe1C&rsv_pq=9c3bda530009489f&rsv_n=2&rsv_sug3=20&rsv_sug2=0&rsv_sug4=669'.format(ip)
    m = ip_from_url(url)
    m.save()
    return m
