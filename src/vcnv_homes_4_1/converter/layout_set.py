"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import math
from lib.convert import *
from common.app_object import AppObject
from .code_manager import CodeManager


class LayoutSet(AppObject):
    """
    各部屋の間取り部屋セット
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()
        self.rooms = []

        if room:
            # 洋室
            for i in range(1, 11):
                area = xfloat(room['western_style_room{0}'.format(i)])
                if area > 0:
                    if len(self.rooms) < 10:    # キッチン用に1枠はとっておく
                        self.rooms += [
                            {
                                'area': float_normalize(math.floor(area * 100) / 100),
                                'type_code': '2',
                            },
                        ]
            # 和室
            for i in range(1, 11):
                area = xfloat(room['japanese_style_room{0}'.format(i)])
                if area > 0:
                    if len(self.rooms) < 10:    # キッチン用に1枠はとっておく
                        self.rooms += [
                            {
                                'area': float_normalize(math.floor(area * 100) / 100),
                                'type_code': '1',
                            },
                        ]

            # キッチン
            for i in range(1, 4):
                area = xfloat(room['kitchen{0}'.format(i)])
                if area > 0:
                    id = xstr(room['kitchen_type{0}'.format(i)]['id'])
                    type_code = xstr(CodeManager.get_instance().kitchen_types.get(id))
                    if len(self.rooms) <= 10:
                        self.rooms += [
                            {
                                'area': float_normalize(math.floor(area * 100) / 100),
                                'type_code': type_code,
                            },
                        ]

        return

    def get_layout_room_area(self, index: int):
        """ 間取り部屋帖数 """
        ans = ''

        if index < len(self.rooms):
            data = xfloat(self.rooms[index]['area'])
            ans = float_normalize(data)

        return ans

    def get_layout_room_type_code(self, index: int):
        """ 間取り部屋種別 """
        ans = ''

        if index < len(self.rooms):
            ans = xstr(self.rooms[index]['type_code'])

        return ans

