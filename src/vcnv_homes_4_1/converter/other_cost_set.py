"""
System Name: Vasyworks
Project Name: vcnv_homes
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import math
from lib.convert import *
from common.app_object import AppObject
from common.system_info import SystemInfo


class OtherCostSet(AppObject):
    """
    各部屋のその他費用セット
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()
        self.other_costs = []

        if room:
            # 支払い手数料
            type_id = xint(room['payment_fee_type']['id'])
            if type_id in (10, 20, 30):
                name = xstr(room['payment_fee_type']['name'])
                cost = xint(room['payment_fee'])
                tax_id = xint(room['payment_fee_tax_type']['id'])
                if cost > 0:
                    self.other_costs += [
                        {
                            'name': name,
                            'cost': cost,
                            'tax_id': tax_id,
                        },
                    ]

            # 月額費用
            for i in range(1, 11):
                name = xstr(room['monthly_cost_name{0}'.format(i)])
                cost = xint(room['monthly_cost{0}'.format(i)])
                tax_id = xint(room['monthly_cost_tax_type{0}'.format(i)]['id'])
                if name and cost > 0:
                    self.other_costs += [
                        {
                            'name': name,
                            'cost': cost,
                            'tax_id': tax_id,
                        },
                    ]

            # 初期費用
            for i in range(1, 11):
                name = xstr(room['initial_cost_name{0}'.format(i)])
                cost = xint(room['initial_cost{0}'.format(i)])
                tax_id = xint(room['initial_cost_tax_type{0}'.format(i)]['id'])
                if name and cost > 0:
                    self.other_costs += [
                        {
                            'name': name,
                            'cost': cost,
                            'tax_id': tax_id,
                        },
                    ]

        return

    def get_cost_name(self, index: int):
        """ 費用名 """
        ans = ''

        if index < len(self.other_costs):
            ans = xstr(self.other_costs[index]['name'])

        return ans

    def get_cost(self, index: int):
        """ 費用 """
        ans = ''

        if index < len(self.other_costs):
            cost = xint(self.other_costs[index]['cost'])
            tax_id = xint(self.other_costs[index]['tax_id'])
            if tax_id == 1:
                # 税別の場合は税込計算
                ans = xstr(int(cost * (1 + SystemInfo.get_instance().tax_rate)))
            else:
                ans = xstr(cost)

        return ans
