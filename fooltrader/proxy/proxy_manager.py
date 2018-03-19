# -*- coding: utf-8 -*-

import datetime
import logging
import socket
import subprocess
from contextlib import closing
from urllib.parse import urlsplit

import pandas as pd
import requests

from fooltrader.proxy import get_sorted_proxy_path, get_proxy
from fooltrader.proxy.spiders.proxy_spider_hideme import ProxySpiderHideMe
from fooltrader.settings import DG_PATH, SUPPORT_SOCKS2HTTP, g_socks2http_proxy_items

logger = logging.getLogger(__name__)


# 由于scrapy不支持socks代理(https://github.com/scrapy/scrapy/issues/747)
# 需要做转发的可以使用http://www.delegate.org/documents/
def start_delegate(proxy):
    local_port = find_free_port()
    cmd = '{} ADMIN=nobdoy RESOLV="" -P:{} SERVER=http TIMEOUT=con:15 SOCKS={}:{}'.format(
        DG_PATH, local_port, proxy['ip'], proxy['port'])
    subprocess.Popen(cmd, shell=True)
    return {'ip': '127.0.0.1',
            'port': local_port,
            'location': 'fooltrader',
            'speed': '1',
            'type': 'http',
            'anonymity': 'high'
            }


def stop_delegate(localport):
    cmd = '{} -P:{} -Fkill'.format(DG_PATH, localport)
    subprocess.Popen(cmd, shell=True)


def release_socks2http_proxy():
    for _, item in g_socks2http_proxy_items:
        stop_delegate(item['port'])


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def crawl_proxy():
    # 这是我自己搭的两个socks代理,需要使用的话,替换成自己的哈
    if SUPPORT_SOCKS2HTTP:
        my_1080 = {'ip': '127.0.0.1',
                   'port': 1080,
                   'location': 'fooltrader',
                   'speed': '1',
                   'type': 'socks',
                   'anonymity': 'high'
                   }
        my_1081 = {'ip': '127.0.0.1',
                   'port': 1081,
                   'location': 'fooltrader',
                   'speed': '1',
                   'type': 'socks',
                   'anonymity': 'high'
                   }
        g_socks2http_proxy_items['{}:{}'.format(my_1080['ip'], + my_1080['port'])] = start_delegate(my_1080)

        g_socks2http_proxy_items['{}:{}'.format(my_1081['ip'], + my_1081['port'])] = start_delegate(my_1081)
    # 抓取免费代理
    ProxySpiderHideMe().run()


def sort_proxy(url):
    domain = "{0.netloc}".format(urlsplit(url))

    for protocol in ['http', 'https']:
        df = pd.DataFrame()
        for _, item in get_proxy(protocol).iterrows():
            try:
                start_time = datetime.datetime.now()
                r = requests.get(url, proxies={'http': item['url'],
                                               'https': item['url']}, timeout=60)
                if r.status_code == 200:
                    elapsed_time = datetime.datetime.now() - start_time
                    item['delay'] = elapsed_time
                    logger.info("{} got proxy:{} delay:{}".format(url, item['url'], elapsed_time))
                    df.append(item)

                    df.drop_duplicates(subset=('url'), keep='last')
                    df.sort_values('delay')
                    if len(df.index) == 10:
                        part_name = "{}to{}".format(df.url.iat[0], df.url.iat[9])
                        df.to_csv(get_sorted_proxy_path(domain=domain, protocol=protocol, part_name=part_name),
                                  index=False)
                        df = pd.DataFrame()

            except Exception as e:
                logger.error("{} using proxy:{} error:{}".format(url, item['url'], e))


if __name__ == '__main__':
    # crawl_proxy()
    sort_proxy(
        "http://www.google.com")
