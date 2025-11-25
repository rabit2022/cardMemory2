import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui

from pynput import mouse, keyboard

from ImageGrid import ImageGrid
from settings import cfg


# ================ 原主类 ========t========
class ReplicateHelper:
    def __init__(self):
        self.is_listening = False

        # GUI
        self.root = tk.Tk()
        self.root.title("Replicate 游戏助手")
        self.root.attributes('-topmost', True)
        win_size_x = int(cfg.CARD_SIZE_X * cfg.GRID_COLS * cfg.DISP_SCALE)
        win_size_y = int(cfg.CARD_SIZE_Y * cfg.GRID_ROWS* cfg.DISP_SCALE)
        self.root.geometry(f"{win_size_x + 40}x{win_size_y + 80}")

        self.status_var = tk.StringVar(value="按 'T' 开始监听 | 按 'Y' 重置 | 游戏内左键翻牌")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)

        # 网格控件
        disp_sz = (int(cfg.CARD_SIZE_X * cfg.DISP_SCALE),int(cfg.CARD_SIZE_Y * cfg.DISP_SCALE))
        self.grid = ImageGrid(self.root, rows=cfg.GRID_ROWS, cols=cfg.GRID_COLS, size=disp_sz)
        self.grid.widget().pack()

        # 监听
        mouse.Listener(on_click=self.on_click).start()
        keyboard.Listener(on_press=self.on_press).start()

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
        # disp_sz = int(cfg.CARD_SIZE_X * cfg.DISP_SCALE)
        disp_sz = (int(cfg.CARD_SIZE_X * cfg.DISP_SCALE),int(cfg.CARD_SIZE_Y * cfg.DISP_SCALE))

        win_w = disp_sz * cfg.GRID_COLS + 40  # 左右边距
        win_h = disp_sz * cfg.GRID_ROWS + 80  # 上下边距（含状态栏）
        # 4. 实例化新网格
        self.grid = ImageGrid(self.root, rows=cfg.GRID_ROWS, cols=cfg.GRID_COLS, size=disp_sz)
        self.grid.widget().pack()
        # 5. 立即调整窗口大小并放回原来位置
        self.root.geometry(f"{win_w}x{win_h}+{geom.split('+')[1]}+{geom.split('+')[2]}")

    # ---------- 鼠标 ----------
    def on_click(self, x, y, button, pressed):
        if not (pressed and self.is_listening): return
        if x < cfg.BOARD_START_X or y < cfg.BOARD_START_Y: return

        # 获取格子坐标
        c = int((x - cfg.BOARD_START_X) / cfg.CARD_STRIDE_X)
        r = int((y - cfg.BOARD_START_Y) / cfg.CARD_STRIDE_Y)
        if not (0 <= c < cfg.GRID_COLS and 0 <= r < cfg.GRID_ROWS): return

        if button == mouse.Button.left:
            threading.Thread(target=self.process_capture, args=(r, c)).start()
        elif button == mouse.Button.right:
            self.root.after(0, lambda: self.grid.clear_image(r, c))

    # ---------- 截图 ----------
    def process_capture(self, r, c):
        time.sleep(cfg.FLIP_DELAY)
        x = cfg.CAPTURE_START_X + c * cfg.CARD_STRIDE_X
        y = cfg.CAPTURE_START_Y + r * cfg.CARD_STRIDE_Y
        img = pyautogui.screenshot(region=(x, y, cfg.CAPTURE_CARD_SIZE_X, cfg.CAPTURE_CARD_SIZE_Y))
        self.root.after(0, lambda: self.grid.set_image(r, c, img))

    # ---------- 主循环 ----------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ReplicateHelper().run()
