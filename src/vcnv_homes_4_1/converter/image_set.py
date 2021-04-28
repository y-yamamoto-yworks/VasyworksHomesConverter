"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import datetime
from urllib import request
from lib.convert import *
from common.app_object import AppObject
from common.system_info import SystemInfo
from .data_helper import DataHelper


class ImageSet(AppObject):
    """
    各部屋の画像セット
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()

        self.main_building_image = None
        self.layout_image = None
        self.room_images = []
        self.room_image_count = 0
        self.building_images = []

        if room:
            room_images = []
            room_images += room.get('pictures')
            building_images = []
            building_images += room['building'].get('pictures')

            # メイン建物外観
            for image in room_images:
                if image['picture_type']['is_building_exterior']:
                    self.main_building_image = image
                    room_images.remove(image)
                    break
            if not self.main_building_image:
                for image in building_images:
                    if image['picture_type']['is_building_exterior']:
                        self.main_building_image = image
                        building_images.remove(image)
                        break

            # 間取図
            for image in room_images:
                if image['picture_type']['is_layout']:
                    self.layout_image = image
                    room_images.remove(image)
                    break

            # 部屋画像
            self.room_images += room_images

            # 建物画像
            self.building_images += building_images

        return

    @property
    def next_image(self):
        """ 次の画像の取得 """
        ans = None

        if self.main_building_image:
            ans = self.main_building_image
            self.main_building_image = None
        elif self.layout_image:
            ans = self.layout_image
            self.layout_image = None
        elif self.__building_image_is_prioritized and len(self.building_images) > 0:
            ans = self.building_images.pop(0)
        elif len(self.room_images) > 0:
            ans = self.room_images.pop(0)
            self.room_image_count += 1

        if ans:
            self.__download(ans[SystemInfo.get_instance().download_image_url])

        return ans

    @property
    def __building_image_is_prioritized(self):
        """ 建物画像を優先する場合はTrue（内部メソッド） """
        ans = False
        if len(self.room_images) <= 0:
            # 部屋画像が無い場合
            ans = True
        elif 0 < SystemInfo.get_instance().prioritized_room_image_count <= self.room_image_count:
            # 部屋画像の優先数の設定が0より大きく、取得数が優先数を以上になっている場合
            ans = True

        return ans

    @classmethod
    def __download(cls, url):
        """  ファイルのダウンロード（内部メソッド） """
        file_name = DataHelper.get_url_filename(url)
        image_log_path = os.path.join(SystemInfo.get_instance().image_log_dir, file_name)

        if not os.path.exists(image_log_path):
            # 過去に送信した履歴がない場合
            try:
                image = request.urlopen(url).read()
                image_path = os.path.join(SystemInfo.get_instance().image_dir, file_name)

                if not os.path.exists(image_path):
                    # 送信対象ディレクトリにファイルがない場合
                    file = open(image_path, mode='wb')
                    file.write(image)
                    file.close()

                file = open(image_log_path, mode='wb')
                file.write(image)
                file.close()

                del image

            except:
                # エラーファイルをログに出力
                # 未着手
                pass

        return

    @classmethod
    def get_file_url(cls, image):
        """ ダウンロード対象画像のURLを取得 """
        ans = None
        if image:
            ans = image['medium_file_url']
        return ans
