from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtCore import Qt, QRect
import pygetwindow as gw
import win32gui
import time
import ctypes

# 设置 DPI 感知，避免高分辨率屏幕下的缩放问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1 或更高版本
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Windows 8 或更早版本
    except:
        pass

# 不同分辨率对应的尺子长度比例
pixel_len = 546  # 基准长度在 1080p 下
def get_resolution_scale(display_wh):
    # 取出分辨率的宽
    display_w = display_wh.split("x")[0]
    # 根据分辨率的宽来计算比例
    return int(pixel_len * (int(display_w) / 1920))  # 转换为整数

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

        # 获取窗口的客户矩形大小
        client_rect = win32gui.GetClientRect(hwnd)
        client_left, client_top = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
        client_right, client_bottom = win32gui.ClientToScreen(hwnd, (client_rect[2], client_rect[3]))

        width = client_right - client_left
        height = client_bottom - client_top

        return (client_left, client_top, width, height)
    else:
        print(f"未找到窗口: {window_title}")
        return None

class RulerWidget(QWidget):
    def __init__(self, ruler_length, x_offset, y_offset, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 去掉边框并保持在最上方

        blank_space = 15  # 刻度1的左侧空白区域
        #根据分辨率缩放空白区域
        # 定义尺子的长度
        self.ruler_length = int(ruler_length)

        self.blank_space = int(blank_space * (self.ruler_length / pixel_len))

        # 确保所有参数都是整数
        self.setGeometry(int(x_offset), int(y_offset), int(ruler_length) + 20, 80)  # 设置窗口位置和大小

        

    def paintEvent(self, event):
        # 创建画布
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 计算刻度1的位置和刻度40的位置
        num_ticks = 40  # 总刻度数
        tick_interval = self.ruler_length / num_ticks  # 每个刻度的间隔
        x1 = int(self.blank_space + self.ruler_length - tick_interval)  # 刻度1的x坐标
        x40 = int(self.blank_space + self.ruler_length - 47 * tick_interval)  # 刻度40的x坐标

        # 计算背景矩形的宽度
        background_width = x1 - x40
        background_height = 25  # 1080p下背景的高度
        # 根据当前分辨率调整背景的高度
        background_height = int(background_height * (self.ruler_length / pixel_len)) + 5

        # 绘制整个底部背景（用于刻度数字的背景）
        # painter.setBrush(QColor(255, 255, 255, 175))  # 浅灰色半透明背景
        # painter.setPen(Qt.NoPen)
        # painter.drawRect(QRect(x40, int(35 * (self.ruler_length / pixel_len)), background_width - int(self.blank_space + self.ruler_length - 38 * tick_interval), background_height))  # 仅绘制从刻度1到刻度40的背景矩形
        # 创建渐变效果
        gradient = QLinearGradient(x40, 0, x1, 0)  # 从左到右渐变
        gradient.setColorAt(0.1, QColor(197, 227, 91, 175)) 
        gradient.setColorAt(0.5, QColor(80, 211, 191, 175))
        gradient.setColorAt(0.9, QColor(232, 116, 199, 175)) 

        # 绘制渐变背景矩形
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRect(x40, int(35 * (self.ruler_length / pixel_len)), background_width - int(self.blank_space + self.ruler_length - 38 * tick_interval), background_height))  # 仅绘制从刻度1到刻度40的背景矩形

        # 绘制刻度
        font_size = 12
        # 根据当前分辨率调整字体大小
        font_size = int(font_size * (self.ruler_length / pixel_len))
        font = QFont("Arial", font_size, QFont.Bold)
        painter.setFont(font)
        # painter.setPen(QColor(220,220,220))
        painter.setPen(QColor(255-246,255-216,255-248))

        long_line_length = 40  # 长刻度线的长度
        short_line_length = 25  # 短刻度线的长度
        # 根据当前分辨率调整刻度线的长度
        long_line_length = int(long_line_length * (self.ruler_length / pixel_len))
        short_line_length = int(short_line_length * (self.ruler_length / pixel_len))
        for i in range(num_ticks + 1):
            x = int(self.blank_space + self.ruler_length - i * tick_interval)

            # 确保坐标是整数
            # line_length = 35 if i % 5 == 0 else 25
            line_length = long_line_length if i % 5 == 0 else short_line_length

            # 绘制刻度线
            if(i >= 2):
                painter.drawLine(x, 0, x, line_length)

            # 绘制刻度数字
            if i % 5 == 0 and i != 0:  # 不绘制数字为0的刻度
                text = str(i)
                # text_rect = painter.boundingRect(x - 20, 40, 40, 20, Qt.AlignCenter, text) 根据当前分辨率调整刻度数字的y轴位置，1080p下为40
                text_rect = painter.boundingRect(x - 20, int(40 * (self.ruler_length / pixel_len)), 40, 20, Qt.AlignCenter, text)

                # 绘制刻度数字
                # painter.setPen(QColor(220,220,220))
                painter.setPen(QColor(255-246,255-216,255-248))
                painter.drawText(text_rect, Qt.AlignCenter, text)

def create_ruler_for_window(window_title):
    window_info = find_window_and_get_position(window_title)
    if not window_info:
        return  # 如果没有找到窗口，退出

    client_left, client_top, window_width, window_height = window_info

    # 确定分辨率标识符
    resolution = f"{window_width}x{window_height}"

    # 根据分辨率调整尺子的长度
    ruler_length = get_resolution_scale(resolution)

    # 根据窗口的分辨率调整尺子的位置
    target_x = 1176
    target_y = 73
    # 根据实际窗口的分辨率宽高比例调整target_y
    target_y = int(target_y * (window_width / window_height) / (16 / 9))
    # 比例调整
    target_x = int(target_x * (window_width / 1920))
    target_y = int(target_y * (window_height / 1080))

    # 创建并显示尺子窗口
    app = QApplication([])
    ruler_widget = RulerWidget(ruler_length, client_left + target_x, client_top + target_y)
    ruler_widget.show()
    app.exec_()

# 启动程序
if __name__ == "__main__":
    create_ruler_for_window("HeavenBurnsRed")