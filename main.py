import time
import pygetwindow as gw
import win32gui
import ctypes
import tkinter as tk
# from tkinter import ttk

# 设置 DPI 感知，避免高分辨率屏幕下的缩放问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1 or later
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Windows 8 or earlier
    except:
        pass

# 不同分辨率对应的尺子长度比例
pixel_len = 546  # 基准长度在 1080p 下
def get_resolution_scale(display_wh):
    # 取出分辨率的宽
    print(display_wh)
    display_w = display_wh.split("x")[0]
    # 根据分辨率的宽来计算比例
    return pixel_len * (int(display_w) / 1920)


# 寻找指定窗口并获取窗口位置和大小
def find_window_and_get_position(window_title):
    all_windows = gw.getAllTitles()
    # 找到包含指定标题的窗口
    window_titles = [title for title in all_windows if window_title in title]

    if window_titles:
        chosen_window_title = window_titles[0]
        window = gw.getWindowsWithTitle(chosen_window_title)[0]

        # 如果窗口最小化，恢复窗口
        window.restore()
        window.activate()
        time.sleep(0.5)

        hwnd = window._hWnd

        # 获取窗口的客户端矩形大小
        client_rect = win32gui.GetClientRect(hwnd)
        client_left, client_top = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
        client_right, client_bottom = win32gui.ClientToScreen(hwnd, (client_rect[2], client_rect[3]))

        width = client_right - client_left
        height = client_bottom - client_top

        return (client_left, client_top, width, height)
    else:
        print(f"未找到窗口: {window_title}")
        return None

# 创建刻度尺并调整位置
def create_ruler_for_window(window_title):
    window_info = find_window_and_get_position(window_title)
    if not window_info:
        return  # 如果没有找到窗口，退出

    client_left, client_top, window_width, window_height = window_info

    # 确定分辨率标识符
    resolution = f"{window_width}x{window_height}"

    # 根据分辨率调整尺子的长度
    ruler_length = get_resolution_scale(resolution)

    # 隐藏主Tk窗口，避免出现空白窗口
    root = tk.Tk()
    root.withdraw()

    # 根据窗口的分辨率调整尺子的位置
    target_x = 1180
    target_y = 65
    # 根据实际窗口的分辨率宽高比例调整target_y
    target_y = int(target_y * (window_width/window_height)/(16/9))
    # 比例调整
    target_x = int(target_x * (window_width / 1920))
    target_y = int(target_y * (window_height / 1080))

    # 绘制刻度
    num_ticks = 40  # 总刻度数
    tick_interval = ruler_length / num_ticks  # 每个刻度的间隔

    # 创建新的 Tkinter 窗口
    ruler_window = tk.Toplevel(root)
    ruler_window.title(f"Ruler - {resolution}")
    ruler_window.geometry(f"{int(ruler_length + 20)}x80")  # 设置高度为50避免空白
    ruler_window.attributes("-alpha", 0.6)  # 设置透明度
    ruler_window.overrideredirect(True)  # 去掉边框
    ruler_window.attributes("-topmost", True)  # 保持在最上方


    # 创建 Canvas 用于绘制刻度
    canvas = tk.Canvas(ruler_window, width=ruler_length + 20, height=100, bg='white')
    canvas.pack()

    

    for i in range(num_ticks + 1):
        # 从右向左递增刻度
        x = 10 + ruler_length - i * tick_interval

        # 每 5 个刻度标注数字
        if i % 5 == 0:
            canvas.create_line(x, 0, x, 35, fill="black", width=2)
            canvas.create_text(x, 40, text=str(i), fill="black", font=("Arial", 10), anchor="n")  # 使用 anchor="n" 来对齐数字
        else:
            canvas.create_line(x, 0, x, 25, fill="black", width=1)


    # 调整尺子的初始位置
    ruler_window.geometry(f"+{client_left + target_x}+{client_top + target_y}")

    root.mainloop()

# 启动程序
if __name__ == "__main__":
    create_ruler_for_window("HeavenBurnsRed")