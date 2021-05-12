"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import configparser
from lib.convert import *


class SystemInfo:
    """
    システム情報
    """
    _instance = None

    def __init__(self):
        """ コンストラクタ """
        self.app_title = 'Homesコンバータ'

        # コンフィグ設定ファイルからの読み込み
        config_ini = configparser.ConfigParser()
        config_ini.read('config.ini', encoding='utf-8')

        self.api_url = config_ini.get('Application', 'Api_Url').format(
            key=config_ini.get('Application', 'Api_key')
        )
        self.download_image_url = config_ini.get('Application', 'Download_image_url')
        self.prioritized_room_image_count = xint(config_ini.get('Application', 'Prioritized_room_image_count'))
        self.tax_rate = xfloat(config_ini.get('Application', 'Tax_rate'))

        self.csv_version = config_ini.get('Homes', 'Csv_version')
        self.homes_id = config_ini.get('Homes', 'Homes_id')
        self.test_mode = config_ini.get('Homes', 'Test_mode')
        self.panorama_csv_version = config_ini.get('Homes', 'Panorama_csv_version')
        self.panorama_test_mode = config_ini.get('Homes', 'Panorama_test_mode')
        self.panorama_lens_type = config_ini.get('Homes', 'Panorama_lens_type')
        self.trader_company = config_ini.get('Homes', 'Trader_company')
        self.trader_company_tel = config_ini.get('Homes', 'Trader_company_tel')
        self.online_preview = config_ini.get('Homes', 'Online_preview')
        self.online_advice = config_ini.get('Homes', 'Online_advice')
        self.it_description = config_ini.get('Homes', 'It_description')

        del config_ini

        # その他
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        home_dir = os.environ.get('HOME')
        if not home_dir:
            home_dir = os.getenv('HOMEDRIVE') + os.getenv('HOMEPATH')
        data_dir = 'Documents/Convert/Homes/{0}/'.format(self.csv_version).replace('/', os.sep)
        self.output_base_dir = os.path.join(home_dir, data_dir)

        # 賃貸データ用ディレクトリ
        self.output_dir = os.path.join(self.output_base_dir, 'rent/'.replace('/', os.sep))
        self.image_dir = os.path.join(self.output_dir, 'image/'.replace('/', os.sep))
        self.log_dir = os.path.join(self.output_dir, 'log/'.replace('/', os.sep))
        self.image_log_dir = os.path.join(self.log_dir, 'image/'.replace('/', os.sep))

        # パノラマデータ用ディレクトリ
        self.panorama_output_dir = os.path.join(self.output_base_dir, 'panorama/'.replace('/', os.sep))
        self.panorama_image_dir = os.path.join(self.panorama_output_dir, 'image/'.replace('/', os.sep))
        self.panorama_log_dir = os.path.join(self.panorama_output_dir, 'log/'.replace('/', os.sep))
        self.panorama_image_log_dir = os.path.join(self.panorama_log_dir, 'image/'.replace('/', os.sep))

        return

    @classmethod
    def get_instance(cls):
        """コンフィグ設定オブジェクトの生成"""
        if not cls._instance:
            cls._instance = SystemInfo()

        return cls._instance

    @classmethod
    def destroy_instance(cls):
        """ インスタンスの消去 """
        del cls._instance
        return
