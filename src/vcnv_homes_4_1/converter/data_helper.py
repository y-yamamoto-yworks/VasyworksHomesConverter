"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import math
from pyproj import Transformer
from lib.convert import *
from common.system_info import SystemInfo
from .code_manager import CodeManager


class DataHelper:
    """データ加工用ヘルパークラス"""
    @classmethod
    def sanitize(cls, data: str):
        """ 文字列のサニタイジング """
        ans = data

        ans = ans.replace('"', '”')
        ans = ans.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

        ans = ans.replace('%', '％').replace('･', '・')
        ans = ans.replace('%', '％').replace('･', '・')
        ans = ans.replace('【', '（').replace('】', '）')
        ans = ans.replace('(', '（').replace(')', '）')

        ans = ans.replace('Ⅰ', 'I').replace('Ⅱ', 'II').replace('Ⅲ', 'III')
        ans = ans.replace('Ⅳ', 'IV').replace('Ⅴ', 'V').replace('Ⅵ', 'VI')
        ans = ans.replace('Ⅶ', 'VII').replace('Ⅷ', 'VIII').replace('Ⅸ', 'IX')
        ans = ans.replace('Ⅹ', 'X')
        ans = ans.replace('髙', '高').replace('﨑', '崎')

        return ans

    @classmethod
    def get_url_filename(cls, url: str):
        """ URLからファイル名を取得 """
        ans = None
        if url:
            ans = url.rsplit('/', 1)[1]
        return ans

    """
    緯度経度
    """
    @classmethod
    def get_lat_lng(cls, w_lat: float, w_lng: float):
        """ 緯度経度（日本測地系） """
        ans = ''

        if w_lat > 0 and w_lng > 0:
            transformer = Transformer.from_crs(4326, 4301, always_xy=True)
            t_lng, t_lat = transformer.transform(w_lng, w_lat)
            del transformer

            ans = '{0}/{1}'.format(cls.degree_to_dms(t_lat), cls.degree_to_dms(t_lng))

        return ans

    @classmethod
    def degree_to_dms(cls, value: float):
        """ 浮動小数点型の度を度分秒に変換 """
        x, y = math.modf(value)
        d = int(y)
        x, y = math.modf(x * 60)
        m = int(y)
        x, y = math.modf(x * 60)
        s = int(y)
        x, y = math.modf(x * 1000)
        ms = int(y)

        return "{0}.{1}.{2}.{3}".format(d, m, s, ms)
