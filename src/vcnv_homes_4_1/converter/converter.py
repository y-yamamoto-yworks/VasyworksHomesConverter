"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import datetime
from lib.convert import *
from common import Api, AppObject, SystemInfo
from .room_data import RoomData


class Converter(AppObject):
    """
    コンバータ
    """
    progress = None
    progressbar = None

    def __init__(self):
        """ コンストラクタ """
        super().__init__()

        return

    def __del__(self):
        """ デストラクタ """
        if self.is_disposable:
            self.progress = None
            self.progressbar = None

        super().__del__()

        return

    """
    コンバート処理
    """
    def convert(self):
        """コンバートの実行"""
        self.write_progress('データ取得中')
        self.reset_progressbar(1)

        rooms = Api.get_json_data(SystemInfo.get_instance().api_url)
        if not rooms:
            self.write_progress('データ取得失敗')
            raise Exception('データの取得に失敗しました。')

        self.write_progress('データ取得済')

        try:
            self.write_progress('画像ディレクトリ準備中')
            self.reset_progressbar(1)
            self.prepare_image_dir()
            self.write_progress('画像ディレクトリ準備済')

            room_count = xint(rooms['count'])
            self.write_progress('データ加工中： {0}件'.format(room_count))
            self.reset_progressbar(room_count)
            self.output_csv_data(rooms['list'], room_count)
            self.output_sent_file()
            self.write_progress('データ加工済： {0}件： 画面を閉じてください。'.format(room_count))

            del rooms
            return

        except Exception:
            self.write_progress('エラーが発生しました。')
            del rooms
            raise

    def output_csv_data(self, rooms, room_count):
        """ CSVデータ出力 """
        csv_file = None

        try:
            file_path = os.path.join(SystemInfo.get_instance().output_dir, 'homes.csv')
            csv_file = open(file=file_path, mode='w', encoding='shift_jis',)

            # ヘッダー部
            csv_file.write(self.get_header_record())

            # データ部
            if room_count > 0:
                count = 0
                for room in rooms:
                    csv_file.write(self.get_data_record(room))

                    # 進捗表示
                    count += 1
                    self.update_progressbar(count)

            csv_file.close()

            return

        except:
            if csv_file:
                csv_file.close()
            raise Exception('CSVデータ出力に失敗しました。')

    @classmethod
    def output_sent_file(cls):
        """ 物件送信制御ファイルの出力 """
        sent_file = None

        try:
            file_path = os.path.join(SystemInfo.get_instance().output_dir, 'sent')
            sent_file = open(file=file_path, mode='w', encoding='shift_jis',)
            sent_file.close()   # 何も出力しない。

            return

        except:
            if sent_file:
                sent_file.close()
            raise Exception('物件送信制御ファイルの出力に失敗しました。')

    @classmethod
    def prepare_image_dir(cls):
        """ 送信対象画像ディレクトリの準備 """
        # 当日のファイル以外は削除
        today = datetime.date.today()
        for file_name in os.listdir(SystemInfo.get_instance().image_dir):
            file_path = os.path.join(SystemInfo.get_instance().image_dir, file_name)
            try:
                file_date = datetime.date.fromtimestamp(os.path.getmtime(file_path))
                if file_date < today:
                    os.remove(file_path)
            except:
                # 削除に失敗した場合はスルー
                pass

    @classmethod
    def get_header_record(cls):
        """ ヘッダーレコードの取得 """
        ans = '"{0}"'.format('header')  # ヘッダ識別文字列
        ans += ',"{0}"'.format(SystemInfo.get_instance().csv_version)  # バージョン番号
        ans += ',"{0}"'.format('0')  # 処理種別
        ans += ',"{0}"'.format(SystemInfo.get_instance().homes_id)  # HOME'S会員番号
        ans += ',"{0}"'.format('0')  # 文字コード
        ans += ',"{0}"'.format('')  # 画像ファイルパス
        ans += ',"{0}"'.format('0')  # 路線設定パターン
        ans += ',"{0}"'.format('0')  # 書換モード
        ans += ',"{0}"'.format(SystemInfo.get_instance().test_mode)  # テストモード

        ans += '\n'
        return ans

    @classmethod
    def get_data_record(cls, room):
        room_data = None

        try:
            room_data = RoomData(room)
            if room_data.is_forbidden_trader:
                # 掲載禁止業者なら何もしない
                return

            """ データレコードの取得 """
            ans = '"{0}"'.format(room_data.room_code)  # 自社管理物件番号
            ans += ',"{0}"'.format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))  # 自社管理修正日時
            ans += ',"{0}"'.format(datetime.datetime.now().strftime('%Y/%m/%d'))  # 情報掲載期限日
            ans += ',"{0}"'.format('1')  # 公開可否
            ans += ',"{0}"'.format(room_data.is_managed)  # 自社物フラグ
            ans += ',"{0}"'.format('1')  # 状態
            ans += ',"{0}"'.format('')  # 物件種別
            ans += ',"{0}"'.format('0')  # 一括入力フラグ
            ans += ',"{0}"'.format('0')  # 投資用物件
            ans += ',"{0}"'.format(room_data.building_name)  # 建物名・物件名
            ans += ',"{0}"'.format(room_data.building_kana)  # 建物名フリガナ(物件名フリガナ)
            ans += ',"{0}"'.format('1')  # 物件名公開
            ans += ',"{0}"'.format(room_data.building_rooms)  # 総戸数・総区画数
            ans += ',"{0}"'.format('0')  # 空き物件数
            ans += ',"{0}"'.format(room_data.room_no)  # 空き物件内容（部屋番号）
            ans += ',"{0}"'.format(room_data.postal_code)  # 郵便番号
            ans += ',"{0}"'.format(room_data.city_code)  # 所在地コード
            ans += ',"{0}"'.format(room_data.town_address)  # 所在地名称
            ans += ',"{0}"'.format('')  # 所在地詳細_表示部
            ans += ',"{0}"'.format(room_data.house_no)  # 所在地詳細_非表示部
            ans += ',"{0}"'.format(room_data.lat_lng)  # 緯度/経度
            ans += ',"{0}"'.format(room_data.get_railway_code(1))  # 路線1
            ans += ',"{0}"'.format(room_data.get_station_code(1))  # 駅1
            ans += ',"{0}"'.format(room_data.get_bus_stop(1))  # バス停名1
            ans += ',"{0}"'.format(room_data.get_bus_time(1))  # バス時間1
            ans += ',"{0}"'.format(room_data.get_walk_time(1))  # 徒歩距離1
            ans += ',"{0}"'.format(room_data.get_railway_code(2))  # 路線2
            ans += ',"{0}"'.format(room_data.get_station_code(2))  # 駅2
            ans += ',"{0}"'.format(room_data.get_bus_stop(2))  # バス停名2
            ans += ',"{0}"'.format(room_data.get_bus_time(2))  # バス時間2
            ans += ',"{0}"'.format(room_data.get_walk_time(2))  # 徒歩距離2
            ans += ',"{0}"'.format('')  # その他交通
            ans += ',"{0}"'.format('')  # 車所要時間
            ans += ',"{0}"'.format('')  # 地目
            ans += ',"{0}"'.format('')  # 用途地域
            ans += ',"{0}"'.format('')  # 都市計画
            ans += ',"{0}"'.format('')  # 条件・設備/設備(左) 構造・性能・仕様
            ans += ',"{0}"'.format('')  # 土地面積計測方式
            ans += ',"{0}"'.format('')  # 区画面積
            ans += ',"{0}"'.format('')  # 私道負担面積
            ans += ',"{0}"'.format('')  # 私道負担割合(分子/分母)
            ans += ',"{0}"'.format('')  # 土地持分(分子/分母)
            ans += ',"{0}"'.format('')  # セットバック
            ans += ',"{0}"'.format('')  # 条件・設備/設備(左) 構造・性能・仕様
            ans += ',"{0}"'.format('')  # 建ぺい率
            ans += ',"{0}"'.format('')  # 容積率
            ans += ',"{0}"'.format('*')  # 接道状況
            ans += ',"{0}"'.format('*')  # 接道方向1
            ans += ',"{0}"'.format('*')  # 接道間口1
            ans += ',"{0}"'.format('*')  # 接道種別1
            ans += ',"{0}"'.format('*')  # 接道幅員1
            ans += ',"{0}"'.format('*')  # 条件・設備/設備(左) 共有
            ans += ',"{0}"'.format('*')  # 接道方向2
            ans += ',"{0}"'.format('*')  # 条件・設備/設備(左) バス・トイレ
            ans += ',"{0}"'.format('*')  # 接道種別2
            ans += ',"{0}"'.format('*')  # 条件・設備/設備(左) バス・トイレ
            ans += ',"{0}"'.format('*')  # 位置指定道路2
            ans += ',"{0}"'.format('*')  # 接道方向3
            ans += ',"{0}"'.format('*')  # 条件・設備/設備(右) セキュリティ
            ans += ',"{0}"'.format('*')  # 接道種別3
            ans += ',"{0}"'.format('*')  # 接道幅員3
            ans += ',"{0}"'.format('*')  # 位置指定道路3
            ans += ',"{0}"'.format('*')  # 接道方向4
            ans += ',"{0}"'.format('*')  # 接道間口4
            ans += ',"{0}"'.format('*')  # 接道種別4
            ans += ',"{0}"'.format('*')  # 接道幅員4
            ans += ',"{0}"'.format('*')  # 位置指定道路4
            ans += ',"{0}"'.format('')  # 土地権利(借地権種類)
            ans += ',"{0}"'.format('')  # 国土法届出
            ans += ',"{0}"'.format('*')  # 法令上の制限
            ans += ',"{0}"'.format(room_data.structure_code)  # 建物構造
            ans += ',"{0}"'.format('*')  # 建物面積計測方式
            ans += ',"{0}"'.format(room_data.room_area)  # 建物面積・専有面積
            ans += ',"{0}"'.format('')  # 敷地全体面積
            ans += ',"{0}"'.format('')  # 延べ床面積
            ans += ',"{0}"'.format('')  # 建築面積
            ans += ',"{0}"'.format(room_data.building_floors)  # 建物階数(地上)
            ans += ',"{0}"'.format(room_data.building_undergrounds)  # 建物階数(地下)
            ans += ',"{0}"'.format(room_data.build_year_month)  # 築年月
            ans += ',"{0}"'.format(room_data.new_build)  # 新築・未入居フラグ
            ans += ',"{0}"'.format('')  # 管理人
            ans += ',"{0}"'.format('')  # 管理形態
            ans += ',"{0}"'.format('')  # 管理組合有無
            ans += ',"{0}"'.format('')  # 管理会社名
            ans += ',"{0}"'.format(room_data.room_floor)  # 部屋階数
            ans += ',"{0}"'.format(room_data.balcony_area)  # バルコニー面積
            ans += ',"{0}"'.format(room_data.direction_code)  # 向き
            ans += ',"{0}"'.format(room_data.room_count)  # 間取部屋数
            ans += ',"{0}"'.format(room_data.layout_type_code)  # 間取部屋種類
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(0))  # 間取(種類)1
            ans += ',"{0}"'.format(room_data.get_layout_room_area(0))  # 間取(畳数)1
            ans += ',"{0}"'.format('')  # 間取(所在階)1
            ans += ',"{0}"'.format('')  # 間取(室数)1
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(1))  # 間取(種類)2
            ans += ',"{0}"'.format(room_data.get_layout_room_area(1))  # 間取(畳数)2
            ans += ',"{0}"'.format('')  # 間取(所在階)2
            ans += ',"{0}"'.format('')  # 間取(室数)2
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(2))  # 間取(種類)3
            ans += ',"{0}"'.format(room_data.get_layout_room_area(2))  # 間取(畳数)3
            ans += ',"{0}"'.format('')  # 間取(所在階)3
            ans += ',"{0}"'.format('')  # 間取(室数)3
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(3))  # 間取(種類)4
            ans += ',"{0}"'.format(room_data.get_layout_room_area(3))  # 間取(畳数)4
            ans += ',"{0}"'.format('')  # 間取(所在階)4
            ans += ',"{0}"'.format('')  # 間取(室数)4
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(4))  # 間取(種類)5
            ans += ',"{0}"'.format(room_data.get_layout_room_area(4))  # 間取(畳数)5
            ans += ',"{0}"'.format('')  # 間取(所在階)5
            ans += ',"{0}"'.format('')  # 間取(室数)5
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(5))  # 間取(種類)6
            ans += ',"{0}"'.format(room_data.get_layout_room_area(5))  # 間取(畳数)6
            ans += ',"{0}"'.format('')  # 間取(所在階)6
            ans += ',"{0}"'.format('')  # 間取(室数)6
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(6))  # 間取(種類)7
            ans += ',"{0}"'.format(room_data.get_layout_room_area(6))  # 間取(畳数)7
            ans += ',"{0}"'.format('')  # 間取(所在階)7
            ans += ',"{0}"'.format('')  # 間取(室数)7
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(7))  # 間取(種類)8
            ans += ',"{0}"'.format(room_data.get_layout_room_area(7))  # 間取(畳数)8
            ans += ',"{0}"'.format('')  # 間取(所在階)8
            ans += ',"{0}"'.format('')  # 間取(室数)8
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(8))  # 間取(種類)9
            ans += ',"{0}"'.format(room_data.get_layout_room_area(8))  # 間取(畳数)9
            ans += ',"{0}"'.format('')  # 間取(所在階)9
            ans += ',"{0}"'.format('')  # 間取(室数)9
            ans += ',"{0}"'.format(room_data.get_layout_room_type_code(9))  # 間取(種類)10
            ans += ',"{0}"'.format(room_data.get_layout_room_area(9))  # 間取(畳数)10
            ans += ',"{0}"'.format('')  # 間取(所在階)10
            ans += ',"{0}"'.format('')  # 間取(室数)10
            ans += ',"{0}"'.format('')  # 間取り備考
            ans += ',"{0}"'.format(room_data.web_catch_copy)  # 物件の特徴
            ans += ',"{0}"'.format('')  # 物件の特徴_A
            ans += ',"{0}"'.format('')  # 物件の特徴_A
            ans += ',"{0}"'.format(room_data.web_appeal)  # 備考
            ans += ',"{0}"'.format('')  # 備考OEM_A
            ans += ',"{0}"'.format('')  # 備考OEM_B
            ans += ',"{0}"'.format('')  # URL
            ans += ',"{0}"'.format('')  # 社内用メモ
            ans += ',"{0}"'.format(room_data.rent)  # 賃料・価格
            ans += ',"{0}"'.format('1')  # 価格公開フラグ
            ans += ',"{0}"'.format('')  # 価格状態
            ans += ',"{0}"'.format('')  # 税金
            ans += ',"{0}"'.format('')  # 税額
            ans += ',"{0}"'.format('')  # 坪単価
            ans += ',"{0}"'.format(room_data.condo_fees)  # 共益費・管理費
            ans += ',"{0}"'.format('')  # 共益費・管理費 税
            ans += ',"{0}"'.format(room_data.reikin)  # 礼金・月数
            ans += ',"{0}"'.format('')  # 礼金 税
            ans += ',"{0}"'.format(room_data.shikikin)  # 敷金・月数
            ans += ',"{0}"'.format(room_data.hosyokin)  # 保証金・月数
            ans += ',"{0}"'.format('')  # 権利金
            ans += ',"{0}"'.format('')  # 権利金 税
            ans += ',"{0}"'.format('')  # 造作譲渡金
            ans += ',"{0}"'.format('')  # 造作譲渡金 税
            ans += ',"{0}"'.format(room_data.shikibiki)  # 償却・敷引金
            ans += ',"{0}"'.format('')  # 償却時期
            ans += ',"{0}"'.format(room_data.renewal_fee)  # 更新料
            ans += ',"{0}"'.format('')  # 満室時表面利回り
            ans += ',"{0}"'.format('')  # 現行利回り
            ans += ',"{0}"'.format('')  # 住宅保険料
            ans += ',"{0}"'.format(room_data.insurance_span)  # 住宅保険期間
            ans += ',"{0}"'.format('')  # 借地料
            ans += ',"{0}"'.format(room_data.contract_years)  # 契約期間(年)
            ans += ',"{0}"'.format(room_data.contract_months)  # 契約期間(月)
            ans += ',"{0}"'.format('')  # 契約期間(区分)
            ans += ',"{0}"'.format('')  # 修繕積立金
            ans += ',"{0}"'.format('')  # 修繕積立基金
            ans += ',"{0}"'.format(room_data.get_other_cost_name(0))  # その他費用名目1
            ans += ',"{0}"'.format(room_data.get_other_cost(0))  # その他費用1
            ans += ',"{0}"'.format(room_data.get_other_cost_name(1))  # その他費用名目2
            ans += ',"{0}"'.format(room_data.get_other_cost(1))  # その他費用2
            ans += ',"{0}"'.format(room_data.get_other_cost_name(2))  # その他費用名目3
            ans += ',"{0}"'.format(room_data.get_other_cost(2))  # その他費用3
            ans += ',"{0}"'.format('')  # 成約価格
            ans += ',"{0}"'.format('')  # 成約日
            ans += ',"{0}"'.format('')  # 成約税金フラグ
            ans += ',"{0}"'.format('')  # 成約税額
            ans += ',"{0}"'.format(room_data.garage_fee)  # 駐車場料金
            ans += ',"{0}"'.format(room_data.garage_fee_tax_code)  # 駐車場料金 税
            ans += ',"{0}"'.format('')  # 駐車場区分
            ans += ',"{0}"'.format(room_data.garage_distance)  # 駐車場距離
            ans += ',"{0}"'.format('')  # 駐車場空き台数
            ans += ',"{0}"'.format('')  # 駐車場備考
            ans += ',"{0}"'.format('')  # 現況
            ans += ',"{0}"'.format(room_data.live_start_type)  # 引渡/入居時期
            ans += ',"{0}"'.format(room_data.live_start_year_month)  # 引渡/入居年月
            ans += ',"{0}"'.format(room_data.live_start_day)  # 引渡/入居旬
            ans += ',"{0}"'.format(room_data.elementary_school)  # 小学校名
            ans += ',"{0}"'.format(room_data.elementary_school_distance)  # 小学校距離
            ans += ',"{0}"'.format('')  # 小学校 学区コード
            ans += ',"{0}"'.format(room_data.junior_high_school)  # 中学校名
            ans += ',"{0}"'.format(room_data.junior_high_school_distance)  # 中学校距離
            ans += ',"{0}"'.format('')  # 中学校 学区コード
            ans += ',"{0}"'.format(room_data.convenience_distance)  # コンビニ距離
            ans += ',"{0}"'.format(room_data.super_distance)  # スーパー距離
            ans += ',"{0}"'.format(room_data.hospital_distance)  # 総合病院距離
            ans += ',"{0}"'.format('')  # 物件担当者名
            ans += ',"{0}"'.format('6')  # 取引態様
            ans += ',"{0}"'.format(room_data.publish_date)  # 掲載確認日
            ans += ',"{0}"'.format('0')  # 客付
            ans += ',"{0}"'.format('')  # 媒介契約年月日
            ans += ',"{0}"'.format('')  # 仲介手数料
            ans += ',"{0}"'.format('0')  # 分配率(客付分)
            ans += ',"{0}"'.format('0')  # 手数料負担(借主)
            ans += ',"{0}"'.format('')  # 客付け業者へのメッセージ
            ans += ',"{0}"'.format(room_data.trader_company)  # 元付名称
            ans += ',"{0}"'.format('')  # 元付郵便番号
            ans += ',"{0}"'.format('')  # 元付所在地コード
            ans += ',"{0}"'.format('')  # 元付所在地詳細
            ans += ',"{0}"'.format(room_data.trader_company_tel)  # 元付電話番号
            ans += ',"{0}"'.format('')  # 元付FAX番号
            ans += ',"{0}"'.format(room_data.trader_company_staff)  # 元付担当者名
            ans += ',"{0}"'.format('')  # 元付備考
            ans += ',"{0}"'.format('')  # オーナー名称
            ans += ',"{0}"'.format('')  # オーナー郵便番号
            ans += ',"{0}"'.format('')  # オーナー所在地コード
            ans += ',"{0}"'.format('')  # オーナー所在地詳細
            ans += ',"{0}"'.format('')  # オーナー電話番号
            ans += ',"{0}"'.format('')  # オーナーFAX番号
            ans += ',"{0}"'.format('')  # オーナー備考
            ans += ',"{0}"'.format('')  # オープンハウス開始日
            ans += ',"{0}"'.format('')  # オープンハウス終了日
            ans += ',"{0}"'.format('')  # オープンハウス実施時間
            ans += ',"{0}"'.format('')  # オープンハウス備考
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名1
            ans += ',"{0}"'.format('')  # ローカル修正日時1
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別1
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント1
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名2
            ans += ',"{0}"'.format('')  # ローカル修正日時2
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別2
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント2
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名3
            ans += ',"{0}"'.format('')  # ローカル修正日時3
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別3
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント3
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名4
            ans += ',"{0}"'.format('')  # ローカル修正日時4
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別4
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント4
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名5
            ans += ',"{0}"'.format('')  # ローカル修正日時5
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別5
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント5
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名6
            ans += ',"{0}"'.format('')  # ローカル修正日時6
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別6
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント6
            ans += ',"{0}"'.format('')  # 所属グループ
            ans += ',"{0}"'.format(room_data.equipment_codes)  # 設備・条件
            ans += ',"{0}"'.format('')  # おすすめポイント数
            ans += ',"{0}"'.format('')  # 容積率制限備考
            ans += ',"{0}"'.format('')  # 建築条件備考
            ans += ',"{0}"'.format('')  # 施工会社名
            ans += ',"{0}"'.format('')  # 建築確認番号
            ans += ',"{0}"'.format(room_data.building_code)  # 自社管理建物番号
            ans += ',"{0}"'.format(room_data.guarantee_fee_type_code)  # 保証会社の利用
            ans += ',"{0}"'.format('')  # 保証会社名
            ans += ',"{0}"'.format(room_data.guarantee_fee)  # 保証会社利用料
            ans += ',"{0}"'.format('')  # 引渡/入居時期相談内容
            ans += ',"{0}"'.format('')  # 特優賃 入居負担額上限
            ans += ',"{0}"'.format('')  # 特優賃 入居負担額下限
            ans += ',"{0}"'.format('')  # 特優賃 料金変動区分
            ans += ',"{0}"'.format('')  # 特優賃 上昇率
            ans += ',"{0}"'.format('')  # 特優賃 家賃補助年数
            ans += ',"{0}"'.format('')  # 特優賃 備考
            ans += ',"{0}"'.format('')  # リフォーム実施年月
            ans += ',"{0}"'.format('')  # リフォーム箇所
            ans += ',"{0}"'.format('')  # リフォーム箇所その他
            ans += ',"{0}"'.format('')  # リフォーム備考
            ans += ',"{0}"'.format(room_data.reform_year_month)  # リノベーション実施年月
            ans += ',"{0}"'.format(room_data.reform_comment)  # リノベーション内容
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名7
            ans += ',"{0}"'.format('')  # ローカル修正日時7
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別7
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント7
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名8
            ans += ',"{0}"'.format('')  # ローカル修正日時8
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別8
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント8
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名9
            ans += ',"{0}"'.format('')  # ローカル修正日時9
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別9
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント9
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名10
            ans += ',"{0}"'.format('')  # ローカル修正日時10
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別10
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント10
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名11
            ans += ',"{0}"'.format('')  # ローカル修正日時11
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別11
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント11
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名12
            ans += ',"{0}"'.format('')  # ローカル修正日時12
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別12
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント12
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名13
            ans += ',"{0}"'.format('')  # ローカル修正日時13
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別13
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント13
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名14
            ans += ',"{0}"'.format('')  # ローカル修正日時14
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別14
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント14
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名15
            ans += ',"{0}"'.format('')  # ローカル修正日時15
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別15
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント15
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名16
            ans += ',"{0}"'.format('')  # ローカル修正日時16
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別16
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント16
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名17
            ans += ',"{0}"'.format('')  # ローカル修正日時17
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別17
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント17
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名18
            ans += ',"{0}"'.format('')  # ローカル修正日時18
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別18
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント18
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名19
            ans += ',"{0}"'.format('')  # ローカル修正日時19
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別19
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント19
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名20
            ans += ',"{0}"'.format('')  # ローカル修正日時20
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別20
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント20
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名21
            ans += ',"{0}"'.format('')  # ローカル修正日時21
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別21
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント21
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名22
            ans += ',"{0}"'.format('')  # ローカル修正日時22
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別22
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント22
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名23
            ans += ',"{0}"'.format('')  # ローカル修正日時23
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別23
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント23
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名24
            ans += ',"{0}"'.format('')  # ローカル修正日時24
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別24
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント24
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名25
            ans += ',"{0}"'.format('')  # ローカル修正日時25
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別25
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント25
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名26
            ans += ',"{0}"'.format('')  # ローカル修正日時26
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別26
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント26
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名27
            ans += ',"{0}"'.format('')  # ローカル修正日時27
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別27
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント27
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名28
            ans += ',"{0}"'.format('')  # ローカル修正日時28
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別28
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント28
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名29
            ans += ',"{0}"'.format('')  # ローカル修正日時29
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別29
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント29
            image = room_data.next_image
            ans += ',"{0}"'.format(room_data.get_image_filename(image))  # ローカルファイル名30
            ans += ',"{0}"'.format('')  # ローカル修正日時30
            ans += ',"{0}"'.format(room_data.get_image_picture_type_code(image))  # 画像種別30
            ans += ',"{0}"'.format(room_data.get_image_comment(image))  # 画像コメント30
            ans += ',"{0}"'.format('')  # 広告料
            ans += ',"{0}"'.format(room_data.structure_addition)  # 建物構造その他
            ans += ',"{0}"'.format(room_data.key_change_cost)  # 鍵交換費用
            ans += ',"{0}"'.format(room_data.cleaning_cost)  # 室内清掃費用
            ans += ',"{0}"'.format(room_data.shopping_street_distance)  # 商店街距離
            ans += ',"{0}"'.format(room_data.drug_store_distance)  # ドラッグストア距離
            ans += ',"{0}"'.format(room_data.park_distance)  # 公園距離
            ans += ',"{0}"'.format(room_data.bank_distance)  # 銀行距離
            ans += ',"{0}"'.format('')  # その他名
            ans += ',"{0}"'.format('')  # その他距離
            ans += ',"{0}"'.format(room_data.include_garage)  # 契約形態
            ans += ',"{0}"'.format(room_data.free_rent_span)  # フリーレント期間
            ans += ',"{0}"'.format(room_data.free_rent_next_month)  # フリーレント賃料発生タイミング
            ans += ',"{0}"'.format('')  # フリーレント備考
            ans += ',"{0}"'.format('')  # カスタマイズ
            ans += ',"{0}"'.format('')  # カスタマイズ
            ans += ',"{0}"'.format('')  # カスタマイズ
            ans += ',"{0}"'.format('')  # 鍵保管場所
            ans += ',"{0}"'.format('')  # 鍵保管場所
            ans += ',"{0}"'.format('')  # 鍵備考
            ans += ',"{0}"'.format('')  # 物件公開区分
            ans += ',"{0}"'.format('')  # 画像ダウンロード許可
            ans += ',"{0}"'.format('1')  # レコード終了マーク
            ans += '\n'

            del room_data
            return ans

        except:
            if room_data:
                del room_data
            raise

    """
    進捗表示用メソッド
    """
    def write_progress(self, message):
        """ 進捗状況の書き込み """
        if self.progress:
            self.progress['text'] = '【{0}】'.format(message)
            self.progress.update()
        return

    def reset_progressbar(self, maximum):
        """ プログレスバーのリセット """
        if self.progressbar:
            self.progressbar['maximum'] = maximum
            self.progressbar.configure(value=0)
            self.progressbar.update()
        return

    def update_progressbar(self, count):
        """ プログレスバーの更新 """
        if self.progressbar:
            self.progressbar.configure(value=count)
            self.progressbar.update()
        return
