import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui

from pynput import mouse, keyboard

# 棋盘起始位置
BOARD_START_X = 915  # 左上角X坐标
BOARD_START_Y = 390  # 左上角Y坐标

# 1130 - 915
CARD_SIZE = 215  # 卡片大小（正方形）
GRID_ROWS = 4  # 行数
GRID_COLS = 4  # 列数

# 1145 - 915
# 卡片之间的间距
CARD_STRIDE = 230  # 卡片间距（包含大小）

# 翻牌等待时间（秒）
FLIP_DELAY = 0.5


class ReplicateHelper:
    def __init__(self):
        self.is_listening = False  # 默认不启动，按下T开启
        self.ui_cards = {}  # 存储UI上的Label组件 (row, col): label
        self.card_images = {}  # 存储卡片的图像对象

        # --- GUI 初始化 ---
        self.root = tk.Tk()
        self.root.title("Replicate 游戏助手")
        self.root.attributes('-topmost', True)  # 置顶

        # 计算窗口大小和初始位置
        self.display_scale = 0.8
        win_w = int(CARD_SIZE * GRID_COLS * self.display_scale)
        win_h = int(CARD_SIZE * GRID_ROWS * self.display_scale)
        self.root.geometry(f"{win_w + 40}x{win_h + 80}")

        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("按 'T' 开始监听 | 按 'Y' 重置 | 游戏内左键翻牌")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            fg="blue",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(pady=5)

        # 卡片容器
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        # 初始化4x4网格
        self.init_grid_ui()

        # --- 鼠标监听 ---
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        # 键盘监听
        self.key_listener = keyboard.Listener(on_press=self.on_press)
        self.key_listener.start()

    def init_grid_ui(self):
        """初始化网格UI组件"""
        # 计算显示用的卡片大小
        disp_size = int(CARD_SIZE * self.display_scale)

        # 创建一个默认的灰色图像
        placeholder = Image.new('RGB', (disp_size, disp_size), color="#cccccc")
        self.default_img = ImageTk.PhotoImage(placeholder)

        # 生成4x4网格的卡片
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                lbl = tk.Label(
                    self.grid_frame,
                    image=self.default_img,
                    borderwidth=2,
                    relief="solid",
                    padx=2,
                    pady=2
                )
                lbl.grid(row=r, column=c, padx=2, pady=2)
                self.ui_cards[(r, c)] = lbl

    def on_press(self, key):
        """键盘按键事件处理"""
        try:
            if hasattr(key, 'char'):
                # 按T键切换监听状态
                if key.char == 't':
                    self.is_listening = not self.is_listening
                    if self.is_listening:
                        state = "监听中（左击翻牌，右键标记）"
                        color = "green"
                    else:
                        state = "已暂停（按T启动）"
                        color = "red"
                    self.root.after(0, lambda: self.status_label_update(state, color))

                # 按Y键重置所有卡片
                elif key.char == 'y':
                    self.root.after(0, self.reset_all)
        except Exception as e:
            print(f"按键处理错误: {e}")

    def status_label_update(self, text, color):
        """更新状态标签文本和颜色"""
        self.status_var.set(text)
        self.status_label.config(fg=color)

    def reset_all(self):
        """重置所有卡片显示"""
        for key in self.ui_cards:
            self.ui_cards[key].config(image=self.default_img)
        self.card_images.clear()
        print("已重置所有卡片")

    def clear_slot(self, row, col):
        """清除指定位置的卡片显示"""
        if (row, col) in self.ui_cards:
            self.ui_cards[(row, col)].config(image=self.default_img)

    def on_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        # 只处理按下状态且处于监听模式
        if not pressed or not self.is_listening:
            return

        # 判断点击是否在棋盘区域内
        if x < BOARD_START_X or y < BOARD_START_Y:
            return

        # 计算相对棋盘的坐标
        rel_x = x - BOARD_START_X
        rel_y = y - BOARD_START_Y

        # 计算点击的行列索引
        col = int(rel_x / CARD_STRIDE)
        row = int(rel_y / CARD_STRIDE)

        # 检查行列是否在有效范围内
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            # 左键点击：处理卡片截图
            if button == mouse.Button.left:
                # 启动线程处理截图（避免UI卡顿）
                threading.Thread(target=self.process_capture, args=(row, col)).start()
            # 右键点击：清除指定位置卡片
            elif button == mouse.Button.right:
                self.root.after(0, lambda: self.clear_slot(row, col))

    def process_capture(self, row, col):
        """处理卡片截图并更新UI"""
        # 等待翻牌动画完成
        time.sleep(FLIP_DELAY)

        # 计算卡片左上角坐标
        cell_x = BOARD_START_X + col * CARD_STRIDE
        cell_y = BOARD_START_Y + row * CARD_STRIDE

        # 截取卡片区域图像
        region = (cell_x, cell_y, CARD_SIZE, CARD_SIZE)
        shot = pyautogui.screenshot(region=region)

        # 调整图像大小以适应UI显示
        disp_size = int(CARD_SIZE * self.display_scale)
        shot_resized = shot.resize((disp_size, disp_size), Image.Resampling.LANCZOS)

        # 在UI线程中更新卡片显示
        self.root.after(0, lambda: self.update_slot(row, col, shot_resized))

    def update_slot(self, row, col, image):
        """更新指定位置的卡片图像"""
        # 转换为Tkinter可用的图像格式
        tk_img = ImageTk.PhotoImage(image)
        self.card_images[(row, col)] = tk_img  # 保持引用避免被回收

        # 更新UI显示
        if (row, col) in self.ui_cards:
            self.ui_cards[(row, col)].config(image=tk_img)

    def run(self):
        """启动主循环"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ReplicateHelper()
    app.run()