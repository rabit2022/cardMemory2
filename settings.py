#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Project  : cardMemory
# @File     : settings.py
# @Time     : 2025/11/25 14:32
# @Author   : admin
# @Version  : python3.8
# @IDE      : PyCharm
import json
import os
from itertools import cycle

_CFG_FILE = os.path.join(os.path.dirname(__file__), 'profiles.json')


class Cfg:
    """单例配置对象"""
    # 棋盘起始位置
    BOARD_START_X = 603  # 左上角X坐标
    BOARD_START_Y = 460  # 左上角Y坐标

    # 1130 - 915
    CARD_SIZE_X = 802 - 603  # 卡片大小（正方形）
    CARD_SIZE_Y = 728 - 460  # 卡片大小（正方形）

    GRID_ROWS = 2  # 行数
    GRID_COLS = 6  # 列数

    # 1145 - 915
    # 卡片+卡片间距= 卡片的版面大小
    CARD_STRIDE_X = 836 - 603  # 卡片间距（包含大小）
    CARD_STRIDE_Y = 783 - 460  # 卡片间距（包含大小）

    # 选中时，放大效果
    # 603,460,,,,795,728  ----- 192,268
    # 568,370,,,,828,750  ----- 260,380
    # 35,90
    CAPTURE_START_X = 568
    CAPTURE_START_Y = 370

    CAPTURE_CARD_SIZE_X = 828 -568
    CAPTURE_CARD_SIZE_Y = 750 -370


    # 网格大小
    DISP_SCALE = 0.5

    # 翻牌等待时间（秒）,固定
    FLIP_DELAY = 0.5

    PROFILES = {}

    @staticmethod
    def _load_json():
        if not os.path.isfile(_CFG_FILE):
            raise FileNotFoundError(f'缺少配置文件 {_CFG_FILE}')
        with open(_CFG_FILE, encoding='utf-8') as f:
            return json.load(f)

    def __init__(self):

        pass

    def init(self):
        self.PROFILES = Cfg._load_json()

        # 生成循环迭代器
        self._key_cycle = cycle(self.PROFILES.keys())
        self.profile = next(self._key_cycle)  # 先拿到第一个
        self.update(self.profile)

    def update(self, name: str):
        if name not in self.PROFILES:
            raise ValueError(f'未知配置 {name}')
        cfg = self.PROFILES[name]
        # 把字典全部变成对象属性
        self.__dict__.update(cfg)
        self.profile = name
        print(f'配置已切换到 {name}')

    def next(self):
        """切到下一个配置（循环）"""
        self.profile = next(self._key_cycle)
        self.update(self.profile)
        return self.profile


# 全局单例，任何地方「import settings」后通过 settings.cfg 访问
cfg = Cfg()

if __name__ == '__main__':
    print(cfg.DISP_SCALE)
    cfg.next()
    print(cfg.DISP_SCALE)
