# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Project : cardMemory
# @File    : test.py
# @Time    : 2025/11/25 21:14
# @Author  : admin
# @Version : python3.8
# @IDE     : PyCharm
# @Origin  :
# @Description: $END$
from shapely.geometry import Point

from settings import cfg


def cell_at(mouse_x: float, mouse_y: float) -> tuple[int, int]:
    """返回鼠标所在的逻辑格子 (col, row)"""
    # 棋盘原点
    origin = Point(cfg.BOARD_START_X, cfg.BOARD_START_Y)
    # 步长向量（X 方向、Y 方向）
    step_x = Point(cfg.CARD_STRIDE_X, 0)
    step_y = Point(0, cfg.CARD_STRIDE_Y)

    # 鼠标坐标 → 向量
    mouse = Point(mouse_x, mouse_y)
    # 相对棋盘原点的偏移
    delta = mouse - origin

    # 向量点积 → 走了多少格
    c = int(delta.dot(step_x) / step_x.dot(step_x))   # 等价于 (x - ox)/stride_x
    r = int(delta.dot(step_y) / step_y.dot(step_y))   # 等价于 (y - oy)/stride_y

    return c, r

if __name__ == '__main__':
    x=1000
    y=200
    c, r = cell_at(x, y)