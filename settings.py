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

from defined.Point import Point

_CFG_FILE = os.path.join(os.path.dirname(__file__), 'profiles.json')


# ---------- 工具：把 JSON 里所有 [x,y] → Point ----------
def _deep_point(data):
    """递归把 list[x,y] → Point，其余保持不动"""
    if isinstance(data, list) and len(data) == 2 and all(isinstance(i, (int, float)) for i in data):
        return Point(*data)
    if isinstance(data, dict):
        return {k: _deep_point(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_deep_point(i) for i in data]
    return data

class Cfg:
    """单例配置对象"""
    _CFG_FILE = _CFG_FILE
    # 棋盘起始位置,左上角坐标
    TOP_LEFT = Point(915,397)
    RIGHT_BOTTOM = Point(1127,610)
    NEXT_CARD_TOP_LEFT = Point(1144,625)

    CAPTURE_TOP_LEFT = Point(915,397)
    CAPTURE_RIGHT_BOTTOM = Point(1127,610)
    NEXT_CARD_CAPTURE_TOP_LEFT = Point(1144,625)

    # GRID_ROWS = 2  # 行数
    # GRID_COLS = 6  # 列数

    GRID_ROWS = 4  # 行数
    GRID_COLS = 4  # 列数

    # 网格大小
    # DISP_SCALE = 0.5
    DISP_SCALE = 0.7

    # 翻牌等待时间（秒）,固定
    FLIP_DELAY = 0.5

    PROFILES = {}

    # 左上角
    @property
    def BOARD_START(self):
        return self.TOP_LEFT

    # 卡片的大小
    @property
    def CARD_SIZE(self):
        return self.RIGHT_BOTTOM - self.TOP_LEFT

    # 卡片+卡片间距= 卡片的版面大小
    @property
    def CARD_PITCH(self):
        return self.NEXT_CARD_TOP_LEFT - self.TOP_LEFT

    @property
    def CAPTURE_START(self):
        return self.CAPTURE_TOP_LEFT

    @property
    def CAPTURE_SIZE(self):
        return self.CAPTURE_RIGHT_BOTTOM - self.CAPTURE_TOP_LEFT

    @property
    def CAPTURE_PITCH(self):
        return self.NEXT_CARD_CAPTURE_TOP_LEFT - self.CAPTURE_TOP_LEFT

    # ---------- 加载 & 切换 ----------
    @staticmethod
    def _load_json():
        if not os.path.isfile(_CFG_FILE):
            raise FileNotFoundError(f'缺少配置文件 {_CFG_FILE}')
        with open(_CFG_FILE, encoding='utf-8') as f:
            return _deep_point(json.load(f))  # ← 1. 深度转 Point

    def __init__(self):
        self.init()

    def init(self):
        self.PROFILES = Cfg._load_json()
        self._key_cycle = cycle(self.PROFILES.keys())
        self.profile = next(self._key_cycle)
        self.update(self.profile)

    def update(self, name: str):
        if name not in self.PROFILES:
            raise ValueError(f'未知配置 {name}')
        cfg = self.PROFILES[name]
        # 把 JSON 里已经转好的 Point / 标量 一次性写进实例
        self.__dict__.update(cfg)
        self.profile = name
        print(f'配置已切换到 {name}')

    def next(self):
        self.profile = next(self._key_cycle)
        self.update(self.profile)
        return self.profile


# 全局单例，任何地方「import settings」后通过 settings.cfg 访问
cfg = Cfg()

if __name__ == '__main__':
    print(cfg.TOP_LEFT)
    cfg.next()
    print(cfg.TOP_LEFT)
