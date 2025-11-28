import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui

from pynput import mouse, keyboard

from ImageGrid import ImageGrid
from SettingsPanel import SettingsPanel
from defined.Point import Point
from settings import cfg


# ================ 原主类 ========t========
class ReplicateHelper:
    def __init__(self):
        self.is_listening = False

        # GUI
        self.root = tk.Tk()
        self.root.title("Replicate 游戏助手")
        self.root.attributes('-topmost', True)

        win_size = (cfg.CARD_SIZE * Point(cfg.GRID_COLS, cfg.GRID_ROWS) * cfg.DISP_SCALE).int()
        self.root.geometry(f"{win_size.x + 40}x{win_size.y + 80}")

        self.status_var = tk.StringVar(value="按 'T' 开始监听 | 按 'Y' 重置 | 游戏内左键翻牌")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)

        # 网格控件
        # disp_sz = (int(cfg.CARD_SIZE.x * cfg.DISP_SCALE),int(cfg.CARD_SIZE.y * cfg.DISP_SCALE))
        disp_sz = (cfg.CARD_SIZE * cfg.DISP_SCALE).int()
        self.grid = ImageGrid(self.root, rows=cfg.GRID_ROWS, cols=cfg.GRID_COLS, size=disp_sz)
        self.grid.widget().pack()

        menubar = tk.Menu(self.root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Edit Profiles", command=self.open_settings_panel)
        self.root.config(menu=menubar)

        # 监听
        mouse.Listener(on_click=self.on_click).start()
        keyboard.Listener(on_press=self.on_press).start()

    def open_settings_panel(self):
        if not cfg.PROFILES:  # 防未初始化
            # msg.showwarning("提示", "配置尚未加载")
            print("提示", "配置尚未加载")
            return
        SettingsPanel(self.root, cfg)

    # ---------- 键盘 ----------
    def on_press(self, key):
        try:
            if hasattr(key, 'char'):
                if key.char == 't':
                    self.is_listening = not self.is_listening
                    txt, color = (("监听中", "green") if self.is_listening else ("已暂停", "red"))
                    self.root.after(0, lambda: self.status_var.set(txt) or self.status_label.config(fg=color))
                elif key.char == 'y':
                    self.root.after(0, self.grid.reset_all)
                elif key.char == 'p':  # ← 新增
                    new_profile_name = cfg.next()
                    # 实时更新网格 & 状态提示
                    self.root.after(0, self.rebuild_grid)
                    self.root.after(0, lambda: self.status_var.set(f"已切换到配置 {new_profile_name}"))
        except Exception as e:
            print(e)

    def rebuild_grid(self):
        # 1. 记录当前窗口位置
        geom = self.root.winfo_geometry()  # 例如 "300x200+1000+500"
        # 2. 销毁旧网格
        self.grid.widget().destroy()
        # 3. 重新计算期望尺寸
        # disp_sz = (int(cfg.CARD_SIZE.x * cfg.DISP_SCALE),int(cfg.CARD_SIZE.y * cfg.DISP_SCALE))
        disp_sz: Point = (cfg.CARD_SIZE * cfg.DISP_SCALE).int()

        win_size: Point = disp_sz * Point(cfg.GRID_COLS, cfg.GRID_ROWS) + Point(40, 80)

        # 4. 实例化新网格
        self.grid = ImageGrid(self.root, rows=cfg.GRID_ROWS, cols=cfg.GRID_COLS, size=disp_sz)
        self.grid.widget().pack()
        # 5. 立即调整窗口大小并放回原来位置
        self.root.geometry(f"{win_size.x}x{win_size.y}+{geom.split('+')[1]}+{geom.split('+')[2]}")

    # ---------- 鼠标 ----------
    def on_click(self, x, y, button, pressed):
        if not (pressed and self.is_listening): return
        if x < cfg.BOARD_START.x or y < cfg.BOARD_START.y: return

        # 获取格子坐标
        mousePos: Point = Point(x, y)
        gridPos = self.to_grid_pos(mousePos)
        if not (0 <= gridPos.x < cfg.GRID_COLS and 0 <= gridPos.y < cfg.GRID_ROWS): return

        if button == mouse.Button.left:
            threading.Thread(target=self.process_capture, args=(gridPos.x, gridPos.y)).start()
        elif button == mouse.Button.right:
            self.root.after(0, lambda: self.grid.clear_image(gridPos.y, gridPos.x))

    def to_grid_pos(self, mousePos: Point) -> Point:
        # (mousePos - start ) / pitch = gridPos
        gridPos: Point = ((mousePos - cfg.BOARD_START) * cfg.CARD_PITCH.inv()).int()
        return gridPos

    def to_mouse_pos(self, gridPos: Point) -> Point:
        # top_left =  (start + gridPos * pitch )
        # top_left = cfg.BOARD_START + gridPos*cfg.CARD_PITCH
        top_left = cfg.CAPTURE_START  + gridPos*cfg.CAPTURE_PITCH
        top_left = top_left.int()
        return top_left

    # ---------- 截图 ----------
    def process_capture(self, c, r):
        time.sleep(cfg.FLIP_DELAY)
        gridPos = Point(c, r)
        top_left = self.to_mouse_pos(gridPos)
        # size = cfg.CARD_PITCH
        size = cfg.CAPTURE_SIZE
        img = pyautogui.screenshot(region=(top_left.x, top_left.y, size.x, size.y))
        self.root.after(0, lambda: self.grid.set_image(r, c, img))

    # ---------- 主循环 ----------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ReplicateHelper().run()
