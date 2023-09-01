import sys
import time
from typing import Tuple
import keyboard
import psutil
import PySide2
from PySide2.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QRect
from PySide2.QtGui import QPainter, QPen, QIcon, QColor, QGuiApplication, QFont
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSystemTrayIcon, \
    QMenu, QAction, QDialog, QMessageBox

from setting import SettingWidget


def getSuitableForm(n: int) -> str:
    """计算得到网速应换算成的单位，如: kb/s, mb/s 等"""
    if n < 1024:
        return f'{n} b/s'
    elif n < 1024 ** 2:
        return f'{n / 1024:.2f} kb/s'
    else:
        return f'{n / 1024 ** 2:.2f} mb/s'


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        print('Hello PySide2!')
        self.action_quit = None
        self.action_about = None
        self.action_setting = None

        self._menu = None
        self._font = None
        self._offsetY = None
        self._offsetX = None
        self.screen_width = QGuiApplication.primaryScreen().geometry().width()
        self.memory_percent = None
        self.cpu_percent = None
        self.up_stream = None
        self.down_stream = None
        self.real_time = None
        self.tray = None
        self._left_button_pressing = False
        self.up = 0  # 上行流量，初值为0
        self.down = 0  # 下行流量，初值为0
        self.oldPos = QPoint(0, 0)

        self.setting = SettingWidget()
        self.setting.setting_changed.connect(self.on_change_setting)
        self.initUI()  # 初始化UI

        self.timer = QTimer()
        self.timer.timeout.connect(self.change_labels_text)
        self.timer.start(1000)

        self.show()

    def __del__(self):
        print('Goodbye PySide2!')

    def initUI(self):
        # self.setGeometry(100, 100, 260, 120)
        self.resize(260, 120)
        # 窗口移动到屏幕中央
        _q_rect = self.frameGeometry()
        center_point = QGuiApplication.primaryScreen().geometry().center()
        _q_rect.moveCenter(center_point)
        self.move(_q_rect.topLeft())

        self.setWindowTitle("实时流量监控")

        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        # self.setStyleSheet(
        #     "QLabel{color: black; font-size:15px;font-family:楷体;};")
        self._font = QFont()
        self._font.setFamily('楷体')
        self._font.setPixelSize(15)
        self.real_time = QLabel('当前时间:', self)  # 时间标签
        self.up_stream = QLabel('上传: kb/s', self)  # 上行流量显示标签
        self.down_stream = QLabel('下载: kb/s', self)  # 下行流量显示标签
        self.cpu_percent = QLabel('CPU利用率：', self)  # cpu利用率标签
        self.memory_percent = QLabel('内存：', self)
        self.real_time.setFont(self._font)
        self.up_stream.setFont(self._font)
        self.down_stream.setFont(self._font)
        self.cpu_percent.setFont(self._font)
        self.memory_percent.setFont(self._font)
        vl = QVBoxLayout()
        vl.addWidget(self.real_time)
        vl.addWidget(self.up_stream)
        vl.addWidget(self.down_stream)
        vl.addWidget(self.cpu_percent)
        vl.addWidget(self.memory_percent)
        self.setLayout(vl)

        self.round_corners()

        # 创建系统托盘文件并去除任务栏中图标
        tray_icon = QIcon('icon.png')
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(tray_icon)
        self._menu = QMenu()
        self.action_about = self._menu.addAction('Click Me')
        self.action_setting = self._menu.addAction('Setting')
        self.action_quit = self._menu.addAction('Quit')
        self.action_about.triggered.connect(self.show_about)
        self.action_setting.triggered.connect(self.setting.ui.show)
        self.action_quit.triggered.connect(app.quit)
        self.tray.setContextMenu(self._menu)
        self.tray.show()
        self.tray.showMessage('Look At Me', '我在系统托盘哦😃!')

    def get_network_speed(self) -> Tuple[str, str]:
        up_now = psutil.net_io_counters().bytes_sent
        down_now = psutil.net_io_counters().bytes_recv
        up_delta = getSuitableForm(up_now - self.up)
        down_delta = getSuitableForm(down_now - self.down)
        self.up = up_now
        self.down = down_now
        return up_delta, down_delta

    def change_labels_text(self):
        self.real_time.setText(
            '当前时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        up, down = self.get_network_speed()
        self.up_stream.setText('上传: {}'.format(up))
        self.down_stream.setText('下载: {}'.format(down))
        self.cpu_percent.setText(f'CPU利用率：{psutil.cpu_percent()}%')
        self.memory_percent.setText(
            f'内存：{psutil.virtual_memory().used / 1024 ** 3:.2f}GB\t{psutil.virtual_memory().percent}%')

    def round_corners(self):
        radius = 10.0
        path = PySide2.QtGui.QPainterPath()
        path.addRoundedRect(PySide2.QtCore.QRectF(self.rect()), radius, radius)
        mask = PySide2.QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def show_about(self):
        QMessageBox.information(self, '关于', '<b>网速监控</b><br>by <a href="https://www.quiser.top">Quiser</a>')

    def change_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            app.quit()
        elif event.key() == Qt.Key_Return:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: PySide2.QtGui.QMouseEvent) -> None:
        if event.button() == Qt.RightButton:
            self._menu.exec_(event.globalPos())
        elif event.button() == Qt.LeftButton:
            self._offsetX = event.globalX() - self.x()
            self._offsetY = event.globalY() - self.y()
            self._left_button_pressing = True

    def mouseReleaseEvent(self, event: PySide2.QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._left_button_pressing = False

    def mouseMoveEvent(self, event: PySide2.QtGui.QMouseEvent) -> None:
        if self._left_button_pressing:
            self.move(event.globalX() - self._offsetX, event.globalY() - self._offsetY)

    def paintEvent(self, event) -> None:
        # print('paintEvent')
        painter = QPainter(self)
        painter.setOpacity(self.setting.get_opacity())
        # print(painter.opacity())
        painter.setBrush(self.setting.get_color())  # 古董白的rgb值
        painter.setPen(QPen(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())
        self.round_corners()

    def wheelEvent(self, event: PySide2.QtGui.QWheelEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.ControlModifier:

            if event.delta() > 0:
                self.setting.set_width(self.width() + 5)
                self.setting.set_height(self.height() + 5)
            else:
                self.setting.set_width(self.width() - 5)
                self.setting.set_height(self.height() - 5)
            self.on_change_setting()

            # self.round_corners()

    def on_change_setting(self):
        # Opacity change applied in self.paintEvent

        self._font.setFamily(self.setting.get_font())
        self._font.setPixelSize(self.setting.get_fontsize())
        self.real_time.setFont(self._font)
        self.up_stream.setFont(self._font)
        self.down_stream.setFont(self._font)
        self.cpu_percent.setFont(self._font)
        self.memory_percent.setFont(self._font)
        # + 1 and - 1 are to ensure that the entire window is refreshed
        # If only the transparency is changed without changing the window size
        # Only text labels will be refreshed.
        self.resize(self.setting.get_width() + 1, self.setting.get_height())
        self.resize(self.setting.get_width() - 1, self.setting.get_height())

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent) -> None:
        if self.setting.ui.isHidden():
            event.ignore()
        # print(event)
        # event.ignore()
        ...


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyWidget()
    keyboard.add_hotkey('ctrl+space', mw.change_visible)
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
