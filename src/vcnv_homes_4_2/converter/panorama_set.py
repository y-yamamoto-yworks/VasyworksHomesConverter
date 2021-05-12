"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import datetime
from lib.convert import *
from common.app_object import AppObject
from common.system_info import SystemInfo
from .data_helper import DataHelper


class PanoramaSet(AppObject):
    """
    各部屋のパノラマセット
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()

        self.room_panoramas = []
        self.building_panoramas = []

        if room:
            # 部屋パノラマ
            self.room_panoramas += room.get('panoramas')

            # 建物パノラマ
            self.building_panoramas += room['building'].get('panoramas')

        return

    @property
    def next_panorama(self):
        """ 次のパノラマの取得 """
        ans = None

        if len(self.room_panoramas) <= 0 and len(self.building_panoramas) > 0:
            ans = self.building_panoramas.pop(0)
        elif len(self.room_panoramas) > 0:
            ans = self.room_panoramas.pop(0)

        if ans:
            DataHelper.download_image(
                ans['file_url'],
                SystemInfo.get_instance().panorama_image_dir,
                SystemInfo.get_instance().panorama_image_log_dir,
            )

        return ans
