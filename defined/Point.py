# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Project : cardMemory
# @File    : Point.py
# @Time    : 2025/11/25 21:38
# @Author  : admin
# @Version : python3.8
# @IDE     : PyCharm
# @Origin  :
# @Description: $END$

from typing import NamedTuple

class Point(NamedTuple):
    """轻量级 2D 向量，支持常用运算"""
    x: float
    y: float

    # 算术
    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)


    def __truediv__(self, scalar: float) -> 'Point':
        return Point(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar: float) -> 'Point':
        return Point(self.x // scalar, self.y // scalar)

    def __mul__(self, other):
        # number
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        elif isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)
        else:
            # 抛出错误
            raise TypeError("乘法只支持 Point,int or float")

    def inv(self) -> 'Point':
        """返回各分量取倒数的新 Point"""
        if self.x == 0 or self.y == 0:
            raise ZeroDivisionError("分量不能为 0")
        return Point(1.0 / self.x, 1.0 / self.y)

    # 常用工具
    def dot(self, other: 'Point') -> float:
        return self.x * other.x + self.y * other.y

    def round(self, ndigits: int = 0) -> 'Point':
        return Point(round(self.x, ndigits), round(self.y, ndigits))

    def int(self) -> 'Point':
        return Point(int(self.x), int(self.y))

    # 兼容 tkinter/pyautogui 调用
    def tuple(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def __iter__(self):
        yield int(self.x)
        yield int(self.y)

    # def __contains__(self, item):
    #     return item.x

if __name__ == '__main__':
    a =  Point(x=603, y=460)

    print(a)