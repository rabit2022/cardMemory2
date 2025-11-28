# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Project : cardMemory
# @File    : SettingsPanel.py
# @Time    : 2025/11/26 00:54
# @Author  : admin
# @Version : python3.8
# @IDE     : PyCharm
# @Origin  :
# @Description: $END$
import json
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import threading

import pyautogui
from pynput import mouse

from defined.Point import Point


class SettingsPanel(tk.Toplevel):
    """可编辑当前配置、保存回 JSON 的弹窗"""
    def __init__(self, parent, cfg_obj):
        super().__init__(parent)
        self.cfg = cfg_obj
        self.title("Edit Profiles")
        # self.geometry("400x600")
        self.minsize(600,800)  # 最小宽/高
        self.resizable(True, True)  # 允许用户拖拽放大

        # 2. 中心定位（保持不变）
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        # 如果内容超高，再手动限制一次
        self.update_idletasks()
        h = min(self.winfo_reqheight(), 500)  # 最高 500，不够就自然高
        self.geometry(f"{self.winfo_width()}x{h}")

        # 3. 去掉 grab_set() 前面的 resizable(False, False)
        # self.resizable(False, False)  ← 删除这一行
        self.transient(parent)
        self.lift()
        # 4. 模态放在最后，避免吞掉窗口拖拽事件
        self.grab_set()

        # 当前配置名
        self.cur_name = tk.StringVar(value=self.cfg.profile)
        self.entries = {}        # 存 Entry 控件

        self._build_ui()
        self._load_values()

        # 拾取状态：None 表示空闲，否则保存「目标 Entry」
        self._pick_target: tk.Entry | None = None
        self._mouse_listener = None  # 动态钩子

    # ---------- 界面 ----------
    def _build_ui(self):
        # 1. 顶部下拉框
        top = tk.Frame(self)
        top.pack(side='top', fill='x', padx=10, pady=10)
        tk.Label(top, text="Current Profile:").pack(side='left')
        ttk.Combobox(top, textvariable=self.cur_name,
                     values=list(self.cfg.PROFILES.keys()),
                     state='readonly').pack(side='left', padx=5)
        self.cur_name.trace_add('write', self._on_profile_change)

        # 2. 中间：滚动区域（占满剩余空间）
        canvas = tk.Canvas(self, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.inner = tk.Frame(canvas)
        canvas.configure(yscrollcommand=scroll.set)

        # 关键：fill + expand=True，让它吃掉所有多余高度
        canvas.pack(side='top', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # 字段动态生成
        fields = ['TOP_LEFT', 'RIGHT_BOTTOM', 'NEXT_CARD_TOP_LEFT',
                  'CAPTURE_TOP_LEFT', 'CAPTURE_RIGHT_BOTTOM',
                  'NEXT_CARD_CAPTURE_TOP_LEFT', 'DISP_SCALE', 'FLIP_DELAY']
        for f in fields:
            row = tk.Frame(self.inner)
            row.pack(fill='x', padx=5, pady=2)

            tk.Label(row, text=f, width=18, anchor='w').pack(side='left')

            ent = tk.Entry(row, width=15)
            ent.pack(side='left', padx=(0, 5))
            self.entries[f] = ent

            # 只有坐标字段加「拾取」按钮
            if f.endswith(('TOP_LEFT', 'RIGHT_BOTTOM')):
                btn = ttk.Button(row, text='📍',
                                 command=lambda e=ent: self._start_pick(e),
                                 width=3)
                btn.pack(side='left')

            # 重置按钮
            btn_reset = ttk.Button(row, text='🔄',
                                   command=lambda f=f, e=ent: self._reset_field(f, e),
                                   width=3)
            btn_reset.pack(side='left')



        # 3. 底部：按钮条（最后 pack，不 expand，高度固定）
        btn_bar = tk.Frame(self)
        btn_bar.pack(side='bottom', fill='x', pady=10)
        ttk.Button(btn_bar, text="Save", command=self._save).pack(side='right', padx=5)
        ttk.Button(btn_bar, text="Cancel", command=self.destroy).pack(side='right', padx=5)

    def _reset_field(self, field: str, entry: tk.Entry):
        """把该字段重新读回 json 里的值"""
        original = self.cfg.PROFILES[self.cur_name.get()].get(field, "")
        if isinstance(original, Point):
            original = f"{original.x},{original.y}"
        entry.delete(0, 'end')
        entry.insert(0, str(original))


    def _start_pick(self, entry: tk.Entry):
        if self._pick_target:
            return
        self._pick_target = entry
        entry.config(bg='lightyellow')


        # 启动监听
        self._mouse_listener = mouse.Listener(on_click=self._on_pick_click)
        self._mouse_listener.start()

    def _on_pick_click(self, x, y, button, pressed):
        if not pressed or button != mouse.Button.left:
            return
        # 写回输入框
        self._pick_target.delete(0, 'end')
        self._pick_target.insert(0, f"{x},{y}")
        self._stop_pick()

    def _stop_pick(self):
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        self._pick_target.config(bg='white')
        self._pick_target = None

    # ---------- 加载当前配置值 ----------
    def _load_values(self):
        prof = self.cfg.PROFILES[self.cur_name.get()]
        for k, ent in self.entries.items():
            v = prof.get(k, "")
            if isinstance(v, Point):
                v = f"{v.x},{v.y}"
            ent.delete(0, 'end')
            ent.insert(0, str(v))

    # ---------- 切换 profile ----------
    def _on_profile_change(self, *_):
        self._load_values()

    # ---------- 保存 ----------
    def _save(self):
        prof = {}
        for k, ent in self.entries.items():
            raw = ent.get().strip()
            if not raw:
                continue
            # Point 字段 "x,y"
            if k.endswith(('TOP_LEFT', 'RIGHT_BOTTOM', '_SIZE')):
                try:
                    x, y = map(float, raw.split(','))
                    prof[k] = Point(x,y)          # 存回 list，JSON 可序列化
                except ValueError:
                    tk.messagebox.showerror("格式错误", f"{k} 应为 x,y")
                    return

            # 标量字段
            else:
                prof[k] = float(raw) if '.' in raw else int(raw)

        self.cfg.PROFILES[self.cur_name.get()].update(prof)
        # 写回文件
        with open(self.cfg._CFG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cfg.PROFILES, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Saved", "配置已保存！", parent=self)
        self.destroy()