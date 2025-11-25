#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Project  : cardMemory
# @File     : ImageGrid.py
# @Time     : 2025/11/25 13:18
# @Author   : admin
# @Version  : python3.8
# @IDE      : PyCharm
# @Desc     : 拖动图片换位，无按钮

from PIL import Image, ImageTk
import tkinter as tk


class ImageGrid:
    """4×4 可拖动换位的图像网格"""
    def __init__(self, parent, *, rows=4, cols=4, size=(128,128)):
        self.rows, self.cols = rows, cols
        self.size = size
        self.default_img = ImageTk.PhotoImage(
            Image.new("RGB", size, "#cccccc")
        )

        # 数据
        self.tk_imgs = {}          # (r,c) -> ImageTk.PhotoImage
        self.drag_src = None       # (r,c) or None
        self.drag_canvas = None    # 拖动时的半透明预览
        self.drag_photo = None     # 保持引用

        # 主框架
        self.frame = tk.Frame(parent)
        self._build_ui()

        # 全局取消拖动（可选）
        parent.bind_all("<Escape>", self._cancel_drag)

    # ---------- 内部 UI ----------
    def _build_ui(self):
        self.labels = {}
        for r in range(self.rows):
            for c in range(self.cols):
                lbl = tk.Label(self.frame, image=self.default_img,
                               bd=2, relief="solid", cursor="hand2")
                lbl.grid(row=r, column=c, padx=2, pady=2)

                # 左键拖动
                lbl.bind("<Button-1>", lambda e, row=r, col=c: self._start_drag(e, row, col))
                lbl.bind("<B1-Motion>", self._move_drag)
                lbl.bind("<ButtonRelease-1>", self._end_drag)

                # 右键直接重置当前格
                lbl.bind("<Button-3>", lambda e, row=r, col=c: self.clear_image(row, col))

                self.labels[(r, c)] = lbl

    # ---------- 拖动事件 ----------
    def _start_drag(self, event, r, c):
        """按下左键：记录源格、创建半透明预览"""
        if (r, c) not in self.tk_imgs:
            return  # 空格子不允许拖动
        self.drag_src = (r, c)

        # 创建顶层 Canvas 做跟随鼠标的小图
        self.drag_canvas = tk.Canvas(self.frame, width=self.size[0], height=self.size[1],
                                     highlightthickness=0, bd=0)
        # 半透明处理：PIL 生成 50% 透明度缩略图
        pil_copy = self._pil_from_tk(self.tk_imgs[(r, c)]).copy()
        pil_copy = pil_copy.resize((int(self.size[0] * 0.8), int(self.size[1] * 0.8)))
        pil_copy = self._set_alpha(pil_copy, 128)
        self.drag_photo = ImageTk.PhotoImage(pil_copy)
        self.drag_canvas.create_image(0, 0, anchor="nw", image=self.drag_photo)
        self.drag_canvas.place(x=event.x_root - self.frame.winfo_rootx(),
                               y=event.y_root - self.frame.winfo_rooty())

    def _move_drag(self, event):
        """鼠标移动：让预览图跟随"""
        if self.drag_canvas is None:
            return
        x = event.x_root - self.frame.winfo_rootx() - self.size[0] // 2
        y = event.y_root - self.frame.winfo_rooty() - self.size[1] // 2
        self.drag_canvas.place(x=x, y=y)

    def _end_drag(self, event):
        """释放：计算目标格，合法就交换"""
        if self.drag_canvas is None:
            return
        # 销毁预览
        self.drag_canvas.destroy()
        self.drag_canvas = None
        self.drag_photo = None

        # 计算目标行列（相对于 grid 框架）
        x = event.x_root - self.frame.winfo_rootx()
        y = event.y_root - self.frame.winfo_rooty()
        c = x // (self.size[0] + 4)  # padx=2 所以 +4
        r = y // (self.size[1] + 4)
        if not (0 <= c < self.cols and 0 <= r < self.rows):
            return
        if (r, c) == self.drag_src:
            return
        self._swap_images(self.drag_src, (r, c))
        self.drag_src = None

    def _cancel_drag(self, _event):
        """按 Esc 取消拖动"""
        if self.drag_canvas is not None:
            self.drag_canvas.destroy()
            self.drag_canvas = None
            self.drag_photo = None
            self.drag_src = None

    # ---------- 交换/清除/重置 ----------
    def _swap_images(self, src, dst):
        """交换两张图；若目标为空，则搬过去并清空源"""
        src_img = self.tk_imgs.get(src)
        dst_img = self.tk_imgs.get(dst)

        # 目标为空 → 搬移
        if dst_img is None:
            self.tk_imgs[dst] = src_img
            self.labels[dst].config(image=src_img)
            self.clear_image(*src)  # 源格置空
            return

        # 双方都有图 → 正常交换
        self.tk_imgs[src], self.tk_imgs[dst] = dst_img, src_img
        self.labels[src].config(image=dst_img)
        self.labels[dst].config(image=src_img)

    def set_image(self, r, c, pil_img):
        tk_img = ImageTk.PhotoImage(pil_img.resize(self.size, Image.LANCZOS))
        self.tk_imgs[(r, c)] = tk_img
        self.labels[(r, c)].config(image=tk_img)

    def clear_image(self, r, c):
        self.labels[(r, c)].config(image=self.default_img)
        self.tk_imgs.pop((r, c), None)

    def reset_all(self):
        for key in self.labels:
            self.labels[key].config(image=self.default_img)
        self.tk_imgs.clear()
        self._cancel_drag(None)

    # ---------- 小工具 ----------
    @staticmethod
    def _pil_from_tk(tk_img):
        """ImageTk.PhotoImage -> PIL.Image（反向转换）"""
        return ImageTk.getimage(tk_img)

    @staticmethod
    def _set_alpha(pil_img, alpha):
        """给图像加透明度（0-255），返回 RGBA"""
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        r, g, b = pil_img.split()
        a = Image.new('L', pil_img.size, alpha)  # 新建 alpha 层
        return Image.merge('RGBA', (r, g, b, a))


    # ---------- 几何辅助 ----------
    def widget(self):
        return self.frame