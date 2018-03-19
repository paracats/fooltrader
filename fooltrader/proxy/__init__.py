# -*- coding: utf-8 -*-

import os

import pandas as pd

from fooltrader import settings


# 获取存档的代理列表

def get_proxy_dir():
    return os.path.join(settings.FOOLTRADER_STORE_PATH, "proxy")


def get_proxy_path(protocol='http'):
    return os.path.join(get_proxy_dir(), "{}_proxy.csv".format(protocol))


def get_sorted_proxy_path(domain, protocol='http', part_name=None):
    if part_name:
        os.path.join(get_proxy_dir(), domain, "{}_{}_proxy.csv".format(protocol, part_name))
    else:
        return os.path.join(get_proxy_dir(), domain, "{}_proxy.csv".format(protocol))


def get_sorted_proxy(domain, protocol='http'):
    if os.path.exists(get_sorted_proxy_path(domain, protocol=protocol)):
        return pd.read_csv(get_proxy_path(protocol))
    else:
        return pd.DataFrame()


def get_proxy(protocol='http'):
    if os.path.exists(get_proxy_path(protocol)):
        return pd.read_csv(get_proxy_path(protocol))
    else:
        return pd.DataFrame()


def save_proxy(proxies, protocol='http'):
    proxy_df = get_proxy(protocol)
    proxy_df = proxy_df.append(proxies)
    proxy_df.drop_duplicates(subset=('url'), keep='last')
    proxy_df.to_csv(get_proxy_path(protocol), index=False)


if not os.path.exists(get_proxy_dir()):
    os.makedirs(get_proxy_dir())
