"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import math
import datetime
from dateutil.relativedelta import relativedelta
from lib.convert import *
from common.app_object import AppObject
from common.system_info import SystemInfo
from .code_manager import CodeManager
from .data_helper import DataHelper
from .image_set import ImageSet
from .panorama_set import PanoramaSet
from .layout_set import LayoutSet
from .other_cost_set import OtherCostSet


class RoomData(AppObject):
    """
    部屋データ
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()
        self.room = None

        if room:
            self.room = room
            self.image_set = ImageSet(room)
            self.panorama_set = PanoramaSet(room)
            self.layout_set = LayoutSet(room)
            self.other_cost_set = OtherCostSet(room)
        else:
            raise Exception("部屋データが不正です。")

        return

    def __del__(self):
        """ デストラクタ """
        if self.is_disposable:
            del self.image_set
            del self.panorama_set
            del self.layout_set
            del self.other_cost_set

        super().__del__()

        return

    """
    管理情報
    """
    @property
    def is_managed(self):
        """ 自社物フラグ """
        ans = '0'
        if self.room['building']['management_type']['is_own'] or self.room['building']['management_type']['is_entrusted']:
            ans = '1'
        elif xint(self.room['building']['management_type']['id']) == 70:
            # 家主直
            ans = '1'
        elif self.room['is_sublease'] or self.room['is_condo_management'] or self.room['is_entrusted']:
            ans = '1'
        return ans

    @property
    def trader(self):
        """ 賃貸管理他業者 """
        ans = None

        trader = None
        if self.is_managed == '0':      # 先物の物件
            if self.room['is_condo_management'] and xint(self.room['condo_trader']['id']) != 0:
                trader = self.room['condo_trader']
            elif xint(self.room['building']['trader']['id']) != 0:
                trader = self.room['building']['trader']

        if trader:
            if not trader['is_stopped'] and not trader['is_deleted']:
                ans = trader

        return ans

    @property
    def is_forbidden_trader(self):
        """ 他業者物件で掲載禁止業者ならTrue """
        ans = False

        trader = self.trader
        if trader:
            if trader['no_trading'] or trader['no_portal']:
                ans = True

        return ans

    @property
    def trader_company(self):
        """ 他社元付会社名 """
        ans = ''

        if self.is_managed == '0':
            trader = self.trader
            if trader:
                ans = xstr(trader['trader_name'])

            if not ans:
                ans = SystemInfo.get_instance().management_company

        return ans

    @property
    def trader_company_tel(self):
        """ 他社元付会社電話番号 """
        ans = ''

        if self.is_managed == '0':
            trader = self.trader
            if trader:
                ans = xstr(trader['tel1'])

            if not ans:
                ans = SystemInfo.get_instance().management_company_tel

        return ans

    @property
    def trader_company_staff(self):
        """ 他社元付会社担当者 """
        ans = ''

        if self.is_managed == '0':
            ans = '管理担当者'

        return ans

    """
    建物情報
    """
    @property
    def building_code(self):
        """ 建物コード """
        ans = xstr(self.room['building']['building_code'])
        return DataHelper.sanitize(ans)

    @property
    def building_name(self):
        """ 建物名称 """
        ans = xstr(self.room['building']['building_name'])
        return DataHelper.sanitize(ans)

    @property
    def building_kana(self):
        """建物名称カナ"""
        ans = xstr(self.room['building']['building_kana'])
        return DataHelper.sanitize(ans)

    @property
    def building_rooms(self):
        """ 総戸数 """
        ans = xstr(self.room['building']['building_rooms'])
        return DataHelper.sanitize(ans)

    @property
    def postal_code(self):
        """ 郵便番号 """
        ans = xstr(self.room['building']['postal_code'])
        if ans == '':
            ans = '999-9999'
        elif '-' not in ans:
            if len(ans) > 4:
                ans = ans[:3] + '-' + ans[3:]
            elif len(ans) == 3:
                ans = ans + '-0000'

        return DataHelper.sanitize(ans).ljust(8, '0')

    @property
    def city_code(self):
        """ 市区町村コード """
        id = xstr(self.room['building']['city']['id'])
        ans = xstr(CodeManager.get_instance().cities.get(id))
        if not ans:
            ans = '00000000000'
        return ans

    @property
    def town_address(self):
        """ 町域名 """
        ans = xstr(self.room['building']['town_address'])
        return DataHelper.sanitize(ans)

    @property
    def house_no(self):
        """ 番地 """
        ans = xstr(self.room['building']['house_no'])
        if ans == '':
            ans = "99999番地"
        return DataHelper.sanitize(ans)

    @property
    def lat_lng(self):
        """ 緯度経度（日本測地系） """
        w_lat = xfloat(self.room['building']['lat'])    # 世界測地系（WGS84）緯度
        w_lng = xfloat(self.room['building']['lng'])    # 世界測地系（WGS84）経度

        ans = DataHelper.get_lat_lng(w_lat, w_lng)
        return ans

    def get_railway_code(self, index: int):
        """ 沿線コード """
        if index not in (1, 2):
            return ''

        id = xstr(self.room['building']['station' + xstr(index)]['railway']['id'])
        return xstr(CodeManager.get_instance().railways.get(id))

    def get_station_code(self, index: int):
        """ 駅コード """
        if index not in (1, 2):
            return ''

        id = xstr(self.room['building']['station' + xstr(index)]['id'])
        return xstr(CodeManager.get_instance().stations.get(id))

    def get_bus_stop(self, index: int):
        """ バス停名 """
        if index not in (1, 2):
            return ''

        ans = ''
        if xstr(self.room['building']['arrival_type' + xstr(index)]['id']) == '2':   # バス利用
            ans = DataHelper.sanitize(xstr(self.room['building']['bus_stop' + xstr(index)]))

        return ans

    def get_bus_time(self, index: int):
        """ バス時間 """
        if index not in (1, 2):
            return ''

        ans = ''
        if xstr(self.room['building']['arrival_type' + xstr(index)]['id']) == '2':   # バス利用
            ans = xstr(self.room['building']['station_time' + xstr(index)])

        return ans

    def get_walk_time(self, index: int):
        """ 徒歩時間 """
        if index not in (1, 2):
            return ''

        ans = ''
        if xstr(self.room['building']['arrival_type' + xstr(index)]['id']) == '2':   # バス利用
            ans = xstr(self.room['building']['bus_stop_time' + xstr(index)])
        else:
            ans = xstr(self.room['building']['station_time' + xstr(index)])

        return ans

    @property
    def structure_code(self):
        """ 構造コード """
        id = xstr(self.room['building']['structure']['id'])
        return xstr(CodeManager.get_instance().structures.get(id))

    @property
    def structure_addition(self):
        """ 建物構造が「その他」の場合の補足 """
        ans = ''

        if self.structure_code == '9':
            ans = xstr(self.room['building']['structure']['name'])

            comment = DataHelper.sanitize(xstr(self.room['building']['structure_comment']))
            if comment:
                ans += '（{0}）'.format(comment)

        return ans

    @property
    def building_floors(self):
        """ 建物階数（地上） """
        return xstr(self.room['building']['building_floors'])

    @property
    def building_undergrounds(self):
        """ 建物階数（地下） """
        ans = xstr(self.room['building']['building_undergrounds'])
        if ans == '0':
            ans = ''
        return ans

    @property
    def build_year_month(self):
        """ 築年月 """
        ans = '{0}/{1:0>2}'.format(
            xstr(self.room['building']['build_year']),
            xstr(self.room['building']['build_month']),
        )
        return ans

    @property
    def new_build(self):
        """ 新築未入居扱いなら1 """
        ans = '0'
        # システム日付の3ヶ月以内なら1
        today = datetime.date.today()
        new_build_date = today - relativedelta(months=3)
        build_date = datetime.date(
            xint(self.room['building']['build_year']),
            xint(self.room['building']['build_month']),
            1,
        )

        if build_date >= new_build_date:
            ans = '1'

        return ans

    @property
    def convenience_distance(self):
        """ コンビニ距離 """
        return self.__get_facility_distance(10)

    @property
    def super_distance(self):
        """ スーパー距離 """
        return self.__get_facility_distance(20)

    @property
    def drug_store_distance(self):
        """ ドラッグストア距離 """
        return self.__get_facility_distance(30)

    @property
    def shopping_street_distance(self):
        """ 商店街距離 """
        return self.__get_facility_distance(50)

    @property
    def bank_distance(self):
        """ 銀行距離 """
        return self.__get_facility_distance(100)

    @property
    def hospital_distance(self):
        """ 総合病院距離 """
        return self.__get_facility_distance(120)

    @property
    def park_distance(self):
        """ 公園距離 """
        return self.__get_facility_distance(160)

    def __get_facility_distance(self, facility_id):
        """ 周辺施設の距離の取得（内部メソッド） """
        ans = ''

        for item in self.room['building']['facilities']:
            if xint(item['facility']['id']) == facility_id:
                ans = xint(item['distance'])
                break

        return ans

    """
    部屋情報
    """
    @property
    def room_code(self):
        ans = ''
        building_code = xstr(self.room['building']['building_code'])
        room_id = '{:0=7}'.format(xint(self.room["id"]))
        if building_code != '':
            ans = building_code + '-' + room_id
        else:
            ans = room_id

        return DataHelper.sanitize(ans)

    @property
    def room_no(self):
        """ 部屋番号 """
        ans = xstr(self.room['room_no'])
        if ans != '':
            ans += '号室'
        return DataHelper.sanitize(ans)

    @property
    def room_area(self):
        """ 専有面積 """
        data = math.floor(xfloat(self.room['room_area']) * 100) / 100
        ans = float_normalize(data)
        return ans

    @property
    def room_floor(self):
        """ 部屋階数 """
        return xstr(self.room['room_floor'])

    @property
    def balcony_area(self):
        """ バルコニー面積 """
        data = math.floor(xfloat(self.room['balcony_area']) * 100) / 100
        ans = float_normalize(data)
        return ans

    @property
    def direction_code(self):
        """ 向きコード """
        id = xstr(self.room['direction']['id'])
        return xstr(CodeManager.get_instance().directions.get(id))

    @property
    def room_count(self):
        """ 間取り部屋数 """
        return xstr(self.room['layout_type']['room_count'])

    @property
    def layout_type_code(self):
        """ 間取種別コード """
        id = xstr(self.room['layout_type']['id'])
        return xstr(CodeManager.get_instance().layout_types.get(id))

    def get_layout_room_area(self, index: int):
        """ 間取り部屋帖数 """
        return self.layout_set.get_layout_room_area(index)

    def get_layout_room_type_code(self, index: int):
        """ 間取り部屋種別 """
        return self.layout_set.get_layout_room_type_code(index)

    @property
    def web_catch_copy(self):
        """ WEB用キャッチコピー """
        ans = xstr(self.room['web_catch_copy'])
        return DataHelper.sanitize(ans)

    @property
    def web_appeal(self):
        """ WEB用アピール """
        ans = xstr(self.room['web_appeal'])
        return DataHelper.sanitize(ans)

    @property
    def rent(self):
        """ 賃料 """
        return xstr(self.room['rent'])

    @property
    def condo_fees(self):
        """ 共益費 """
        ans = ''

        id = xint(self.room['condo_fees_type']['id'])
        if id == 10:
            ans = xstr(self.room['condo_fees'])
        elif id in (20, 21):
            ans = '0'

        return ans

    @property
    def reikin(self):
        """ 礼金 """
        ans = ''
        type_id = xint(self.room['key_money_type1']['id'])
        if type_id in (10, 11, 12):
            notation_id = xint(self.room['key_money_notation1']['id'])
            value = xstr(self.room['key_money_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2 and xint(value) >= 100:
                ans = value
            elif notation_id == 3 and xfloat(value) < 100:
                ans = value

        return ans

    @property
    def shikikin(self):
        """ 敷金 """
        ans = ''
        type_id = xint(self.room['deposit_type1']['id'])
        if type_id == 10:
            notation_id = xint(self.room['deposit_notation1']['id'])
            value = xstr(self.room['deposit_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2 and xint(value) >= 100:
                ans = value
            elif notation_id == 3 and xfloat(value) < 100:
                ans = value

        return ans

    @property
    def hosyokin(self):
        """ 保証金 """
        ans = ''
        type_id = xint(self.room['deposit_type1']['id'])
        if type_id in (20, 30):
            notation_id = xint(self.room['deposit_notation1']['id'])
            value = xstr(self.room['deposit_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2 and xint(value) >= 100:
                ans = value
            elif notation_id == 3 and xfloat(value) < 100:
                ans = value

        return ans

    @property
    def shikibiki(self):
        """ 敷引・償却金 """
        ans = ''
        type_id = xint(self.room['key_money_type1']['id'])
        if type_id in (20, 21, 22):
            notation_id = xint(self.room['key_money_notation1']['id'])
            value = xstr(self.room['key_money_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2 and xint(value) >= 100:
                ans = value
            elif notation_id == 3 and xfloat(value) < 100:
                ans = value

        return ans

    @property
    def renewal_fee(self):
        """ 更新料 """
        ans = ''

        notation_id = xint(self.room['renewal_fee_notation']['id'])
        value = xstr(self.room['renewal_fee_value'])
        if notation_id == 1:
            ans = '0'
        elif notation_id == 2 and xint(value) >= 100:
            ans = value
        elif notation_id in (3, 4) and xfloat(value) < 100:
            ans = value

        return ans

    @property
    def insurance_span(self):
        """ 火災保険期間 """
        ans = ''

        data = xstr(self.room['insurance_years'])
        if xint(data) > 0:
            ans = data

        return ans

    @property
    def contract_years(self):
        """ 契約期間（年） """
        ans = ''

        data = xstr(self.room['contract_years'])
        if xint(data) > 0:
            ans = data

        return ans

    @property
    def contract_months(self):
        """ 契約期間（月） """
        ans = ''

        data = xstr(self.room['contract_months'])
        if xint(data) > 0:
            ans = data

        return ans

    def get_other_cost_name(self, index: int):
        """ その他費用名 """
        return self.other_cost_set.get_cost_name(index)

    def get_other_cost(self, index: int):
        """ その他費用 """
        return self.other_cost_set.get_cost(index)

    @property
    def garage_fee(self):
        """ 駐車場料金 """
        ans = ''

        id = xint(self.room['building']['garage_type']['id'])
        if id == 1:
            # 駐車場料金が有料の場合
            fee = xint(self.room['building']['garage_fee_lower'])
            upper = xint(self.room['building']['garage_fee_upper'])
            if fee < upper:
                fee = upper

            tax_id = xint(self.room['building']['garage_fee_tax_type']['id'])
            if tax_id == 1:
                fee = int(fee * (1 + SystemInfo.get_instance().tax_rate))

            ans = xstr(fee)

        elif id == 5:
            # 駐車場料金が無料の場合
            ans = '0'

        return ans

    @property
    def garage_fee_tax_code(self):
        """ 駐車場料金税 """
        ans = ''

        id = xint(self.room['building']['garage_type']['id'])
        if id == 1:
            ans = '2'   # 税込

        return ans

    @property
    def garage_distance(self):
        """ 駐車場距離 """
        ans = ''

        if self.room['building']['garage_type']['is_exist']:
            ans = xstr(self.room['building']['garage_distance'])

        return ans

    @property
    def include_garage(self):
        """ ガレージ込みの場合は 1 """
        ans = ''

        id = xint(self.room['building']['garage_type']['id'])
        if id in (3, 4, 5):     # ガレージ込み・付き・無料
            ans = '1'

        return ans

    @property
    def live_start_type(self):
        """ 入居開始時期種別 """
        ans = '2'

        room_status_id = xint(self.room['room_status']['id'])
        vacancy_status_id = xint(self.room['vacancy_status']['id'])
        live_start_year = xint(self.room['live_start_year'])
        live_start_month = xint(self.room['live_start_month'])

        if room_status_id == 1 and vacancy_status_id == 10:
            # 空室で即入居可の場合
            ans = '1'
        elif vacancy_status_id == 80:
            # 入居日相談の場合
            ans = '2'
        elif live_start_year > 0 and live_start_month > 0:
            ans = '3'

        return ans

    @property
    def live_start_year_month(self):
        """  入居可能年月 """
        ans = ''

        if self.live_start_type == '3':
            # 期日指定の場合
            ans = '{0}/{1:0>2}'.format(
                xint(self.room['live_start_year']),
                xint(self.room['live_start_month']),
            )

        return ans

    @property
    def live_start_day(self):
        """ 入居可能旬日 """
        ans = ''

        if self.live_start_type == '3':
            # 期日指定の場合
            id = xstr(self.room['live_start_day']['id'])
            return xstr(CodeManager.get_instance().live_start_month_days.get(id))

        return ans

    @property
    def elementary_school(self):
        """ 小学校名 """
        ans = ''

        id = xint(self.room['building']['elementary_school']['id'])
        distance = xint(self.room['building']['elementary_school_distance'])

        if id != 0 and distance > 0:
            ans = xstr(self.room['elementary_school']['name'])

        return DataHelper.sanitize(ans)

    @property
    def elementary_school_distance(self):
        """ 小学校距離 """
        ans = ''

        id = xint(self.room['building']['elementary_school']['id'])
        distance = xint(self.room['building']['elementary_school_distance'])

        if id != 0 and distance > 0:
            ans = xstr(distance)

        return ans

    @property
    def junior_high_school(self):
        """ 中学校名 """
        ans = ''

        id = xint(self.room['building']['junior_high_school']['id'])
        distance = xint(self.room['building']['junior_high_school_distance'])

        if id != 0 and distance > 0:
            ans = xstr(self.room['junior_high_school']['name'])

        return DataHelper.sanitize(ans)

    @property
    def junior_high_school_distance(self):
        """ 中学校距離 """
        ans = ''

        id = xint(self.room['building']['junior_high_school']['id'])
        distance = xint(self.room['building']['junior_high_school_distance'])

        if id != 0 and distance > 0:
            ans = xstr(distance)

        return ans

    @property
    def publish_date(self):
        return datetime.datetime.today().strftime('%Y/%m/%d')

    @property
    def equipment_codes(self):
        """ 設備 """
        ans = "99900"       # 先頭（設備条件を削除）

        # バス・トイレ別
        id = xint(self.room['bath_type']['id'])
        if id == 4:
            ans = self.__add_equipment_code('20501', ans)

        # 室内洗濯機置き場・室外洗濯機置き場
        id = xint(self.room['washer_type']['id'])
        if id == 10:
            ans = self.__add_equipment_code('21801', ans)
        elif id in (20, 30):
            ans = self.__add_equipment_code('21802', ans)

        # バルコニー・専用庭
        id = xint(self.room['balcony_type']['id'])
        if id in (2, 3):
            ans = self.__add_equipment_code('22701', ans)
        elif id == 4:
            ans = self.__add_equipment_code('22501', ans)

        # internet 対応・光ファイバー対応・インターネット無料
        id = xint(self.room['internet_type']['id'])
        if id == 1:
            ans = self.__add_equipment_code('26301', ans)
        elif id == 2:
            ans = self.__add_equipment_code('23403', ans)
        elif id == 3:
            ans = self.__add_equipment_code('23401', ans)

        # オール電化
        id = xint(self.room['gas_type']['id'])
        if id == 30:
            ans = self.__add_equipment_code('24401', ans)

        # 駐輪場
        if self.room['building']['bike_parking_type']['is_exist']:
            ans = self.__add_equipment_code('23101', ans)

        # バイク置き場
        id = xint(self.room['building']['bike_parking_type']['id'])
        if id in (30, 31, 40, 41, 50, 51):
            ans = self.__add_equipment_code('23201', ans)

        # ペット可・ペット相談
        if self.room['pet_type']['is_ok']:
            ans = self.__add_equipment_code('10901', ans)
        else:
            id = xint(self.room['pet_type']['id'])
            if id == 20:
                ans = self.__add_equipment_code('10902', ans)

        # 分譲賃貸
        id = xint(self.room['building']['building_type']['id'])
        if id == 40:
            ans = self.__add_equipment_code('12201', ans)

        # マンスリー可
        id = xint(self.room['rental_type']['id'])
        if id in (40, 41, 42):
            ans = self.__add_equipment_code('12301', ans)

        # 楽器相談可
        id = xint(self.room['instrument_type']['id'])
        if id in (1, 3):
            ans = self.__add_equipment_code('10001', ans)

        # 二人入居可
        id = xint(self.room['live_together_type']['id'])
        if id in (1, 3):
            ans = self.__add_equipment_code('10301', ans)

        # ルームシェア可
        id = xint(self.room['share_type']['id'])
        if id in (1, 3):
            ans = self.__add_equipment_code('26601', ans)

        # 事務所可
        id = xint(self.room['office_use_type']['id'])
        if id in (1, 3):
            ans = self.__add_equipment_code('10101', ans)

        # 男性限定
        id = xint(self.room['only_man_type']['id'])
        if id == 4:
            ans = self.__add_equipment_code('10401', ans)

        # 女性限定
        id = xint(self.room['only_woman_type']['id'])
        if id == 4:
            ans = self.__add_equipment_code('10402', ans)

        # 法人限定
        id = xint(self.room['corp_contract_type']['id'])
        if id == 4:
            ans = self.__add_equipment_code('10601', ans)


        # その他（設備リストより）
        for item in self.room['equipments']:
            ans = self.__add_equipment_code(
                xstr(CodeManager.get_instance().equipments.get(xstr(item['equipment']['id']))),
                ans,
            )

        return ans

    @classmethod
    def __add_equipment_code(cls, code, codes):
        """ 設備リストに設備を追加（内部メソッド） """
        ans = codes
        if code and len(ans) + len(code) + 1 <= 200:     # 200文字まで
            if ans:
                ans += '/'
            ans += code

        return ans

    @property
    def guarantee_fee_type_code(self):
        """ 保証会社種別コード """
        id = xstr(self.room['guarantee_type']['id'])
        return xstr(CodeManager.get_instance().guarantee_types.get(id))

    @property
    def guarantee_fee(self):
        """ 保証会社利用料 """
        ans = ''

        if self.guarantee_fee_type_code in ('1', '2'):
            ans = DataHelper.sanitize(xstr(self.room['guarantee_fee']))

        if not ans:
            ans = '保証会社利用料は確認が必要。'

        return ans

    @property
    def is_reformed(self):
        """ リフォーム情報がある場合はTrue """
        ans = False

        year = xint(self.room['reform_year'])
        month = xint(self.room['reform_month'])
        comment = xstr(self.room['reform_comment'])

        if year >= 1000 and 1 <= month <= 12 and comment:
            ans = True

        return ans

    @property
    def reform_year_month(self):
        """ リフォーム年月 """
        ans = ''

        if self.is_reformed:
            ans = '{0}/{1:0>2}'.format(
                xstr(self.room['reform_year']),
                xstr(self.room['reform_month']),
            )

        return ans

    @property
    def reform_comment(self):
        """ リフォーム内容コメント """
        ans = ''

        if self.is_reformed:
            ans = DataHelper.sanitize(xstr(self.room['reform_comment']))

        return ans

    @property
    def key_change_cost(self):
        """ 鍵交換費用 """
        ans = ''

        if xint(self.room['key_change_cost_existence']['id']) == 1:     # 有り
            cost = xint(self.room['key_change_cost'])
            if cost > 0:
                tax_id = xint(self.room['key_change_cost_tax_type']['id'])
                if tax_id == 1:
                    cost = int(cost * (1 + SystemInfo.get_instance().tax_rate))
                ans = xstr(cost)

        return ans

    @property
    def cleaning_cost(self):
        """ 退去時清掃費用 """
        ans = ''

        if self.room['cleaning_type']['is_paid']:
            cost = xint(self.room['cleaning_cost'])
            if cost > 0:
                tax_id = xint(self.room['cleaning_cost_tax_type']['id'])
                if tax_id == 1:
                    cost = int(cost * (1 + SystemInfo.get_instance().tax_rate))
                ans = xstr(cost)

        return ans

    @property
    def free_rent_span(self):
        """ フリーレント期間 """
        ans = ''

        id = xint(self.room['free_rent_type']['id'])
        if id == 1:
            months = xint(self.room['free_rent_months'])
            if months > 0:
                ans = xstr(months)

        return ans

    @property
    def free_rent_next_month(self):
        """ フリーレント賃料発生年月 """
        ans = ''

        id = xint(self.room['free_rent_type']['id'])
        if id == 2:
            year = self.room['free_rent_limit_year']
            month = self.room['free_rent_limit_month']
            if year >= datetime.datetime.today().year and 1 <= month <= 12:
                month += 1
                if month > 12:
                    year += 1
                    month = 1

                ans = '{0}/{1:0>2}'.format(
                    xstr(year),
                    xstr(month),
                )

        return ans

    """
    画像情報
    """
    @property
    def next_image(self):
        """ 次の画像の取得 """
        return self.image_set.next_image

    @classmethod
    def get_image_filename(cls, image):
        """ 画像データからファイル名を取得 """
        ans = ''
        if image:
            ans = DataHelper.get_url_filename(image[SystemInfo.get_instance().download_image_url])
        return ans

    @classmethod
    def get_image_picture_type_code(cls, image):
        """ 画像データの画像種別コードを取得 """
        ans = ''
        if image:
            id = xstr(image['picture_type']['id'])
            ans = xstr(CodeManager.get_instance().picture_types[id])
        return ans

    @classmethod
    def get_image_comment(cls, image):
        """ 画像データのコメントを取得 """
        ans = ''
        if image:
            ans = DataHelper.sanitize(xstr(image['comment']))
        return ans

    """
    パノラマ情報
    """
    @property
    def has_panoramas(self):
        """ パノラマがあればTrue """
        ans = False
        if len(self.room['panoramas']) > 0 or len(self.room['building']['panoramas']) > 0:
            return True

        return ans

    @property
    def panorama_local_code(self):
        """ パノラマローカルID（自社管理物件番号と同じ） """
        return self.room_code

    @property
    def publish_panoramas(self):
        """ パノラマ掲載フラグ """
        ans = ''
        if self.has_panoramas:
            ans = '1'

        return ans

    @property
    def panorama_set_name(self):
        ans = self.building_name + ' ' + self.room_no
        return ans

    @property
    def next_panorama(self):
        """ 次のパノラマの取得 """
        return self.panorama_set.next_panorama

    @classmethod
    def get_panorama_filename(cls, panorama):
        """ パノラマデータからファイル名を取得 """
        ans = ''
        if panorama:
            ans = DataHelper.get_url_filename(panorama['file_url'])
        return ans

    @classmethod
    def get_panorama_lens_type(cls, panorama):
        """ パノラマデータのレンズ種別コードを取得 """
        ans = ''
        if panorama:
            ans = SystemInfo.get_instance().panorama_lens_type
        return ans

    @classmethod
    def get_panorama_type_code(cls, panorama):
        """ パノラマデータのパノラマ種別コードを取得 """
        ans = ''
        if panorama:
            id = xstr(panorama['panorama_type']['id'])
            ans = xstr(CodeManager.get_instance().panorama_types[id])
        return ans
