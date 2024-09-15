from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtCore import Qt, QRect, QPoint
import pygetwindow as gw
# import win32gui
# import time
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

class RulerWidget(QWidget):
    def __init__(self, ruler_length, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # 去掉边框并保持在最上方

        self.ruler_length = ruler_length

        self.blank_space = int(15 * (self.ruler_length / pixel_len))

        # 确保所有参数都是整数
        self.setGeometry(100, 100, ruler_length + 20, 80)  # 设置窗口位置和大小

        # 拖动相关变量
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        num_ticks = 40  # 总刻度数
        tick_interval = self.ruler_length / num_ticks  # 每个刻度的间隔
        x1 = int(self.blank_space + self.ruler_length - tick_interval)  # 刻度1的x坐标
        x40 = int(self.blank_space + self.ruler_length - 47 * tick_interval)  # 刻度40的x坐标

        # 计算背景矩形的宽度
        background_width = x1 - x40
        background_height = 25  # 1080p下背景的高度
        background_height = int(background_height * (self.ruler_length / pixel_len)) + 5

        # 创建渐变效果
        gradient = QLinearGradient(x40, 0, x1, 0)  # 从左到右渐变
        gradient.setColorAt(0.0, QColor(255, 0, 0, 175))  # 红色，带透明度
        gradient.setColorAt(1.0, QColor(0, 200, 0, 175))  # 绿色，带透明度

        # 绘制渐变背景矩形
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRect(x40, int(35 * (self.ruler_length / pixel_len)), background_width - int(self.blank_space + self.ruler_length - 38 * tick_interval), background_height))

        # 绘制刻度
        font_size = 12
        font_size = int(font_size * (self.ruler_length / pixel_len))
        font = QFont("Arial", font_size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(246, 216, 248))

        long_line_length = 40
        short_line_length = 25
        long_line_length = int(long_line_length * (self.ruler_length / pixel_len))
        short_line_length = int(short_line_length * (self.ruler_length / pixel_len))

        for i in range(num_ticks + 1):
            x = int(self.blank_space + self.ruler_length - i * tick_interval)
            line_length = long_line_length if i % 5 == 0 else short_line_length

            if i >= 2:
                painter.drawLine(x, 0, x, line_length)

            if i % 5 == 0 and i != 0:
                text = str(i)
                text_rect = painter.boundingRect(x - 20, int(40 * (self.ruler_length / pixel_len)), 40, 20, Qt.AlignCenter, text)
                painter.setPen(QColor(246, 216, 248))
                painter.drawText(text_rect, Qt.AlignCenter, text)

def create_ruler_with_input():
    # 提示用户输入分辨率
    app = QApplication([])

    resolution, ok = QInputDialog.getText(None, '输入分辨率', '请输入分辨率 (格式: 宽x高)：')
    
    if ok and resolution:
        # 根据用户输入的分辨率调整尺子的长度
        ruler_length = get_resolution_scale(resolution)

        ruler_widget = RulerWidget(ruler_length)
        ruler_widget.show()

        app.exec_()

if __name__ == "__main__":
    create_ruler_with_input()
