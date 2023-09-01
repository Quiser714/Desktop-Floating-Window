import PySide2
from PySide2 import QtCore
from PySide2.QtGui import QGuiApplication, Qt, QColor
from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QColorDialog
from PySide2.QtUiTools import QUiLoader


class SettingWidget(QWidget):
    setting_changed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self._color = QColor(250, 235, 215)  # 古董白
        self._fontsize = 15
        self._font = '楷体'
        self._height = 121
        self._width = 260
        self._opacity = 0.7
        self.ui = QUiLoader().load('setting.ui')
        self.initUI()

    def initUI(self):
        self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.ui.ok_btn.clicked.connect(self.update_setting_data)
        self.ui.color_btn.clicked.connect(self.choose_color)
        self.ui.reset_btn.clicked.connect(self.reset_setting_data)
        self.ui.cancel_btn.clicked.connect(self.ui.close)
        self.ui.opacity_value.valueChanged.connect(self._on_opacity_slider_changed)

        ...

    def _on_opacity_slider_changed(self, v):
        self._opacity = v / 100
        self.ui.label.setText(f'透明度({v / 100:.2f})')
        self.setting_changed.emit()

    def choose_color(self):
        color_dialog = QColorDialog()
        color_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        color_dialog.exec_()
        self._color = color_dialog.selectedColor()
        self.setting_changed.emit()

    def get_opacity(self):
        return self._opacity

    def get_width(self):
        return self._width

    def set_width(self, w):
        self._width = w

    def get_height(self):
        return self._height

    def set_height(self, h):
        self._height = h

    def get_font(self):
        return self._font

    def get_fontsize(self):
        return self._fontsize

    def get_color(self):
        return self._color

    def set_color(self, c: QColor):
        self._color = c

    def update_setting_data(self):
        self._opacity = self.ui.opacity_value.value() / 100
        self._width = self.ui.width_value.value()
        self._height = self.ui.height_value.value()
        self._font = self.ui.font_text.currentText()
        self._fontsize = self.ui.fontsize_value.value()
        # self._color is set at the Select-Color button
        self.setting_changed.emit()
        # print(self._opacity, self._width, self._height, self._font, self._fontsize)

    def reset_setting_data(self):
        self._opacity = 0.7
        self._width = 260
        self._height = 121
        self._font = '楷体'
        self._fontsize = 15
        self._color = QColor(250, 235, 215)
        self.ui.opacity_value.setValue(70)
        self.ui.width_value.setValue(260)
        self.ui.height_value.setValue(121)
        self.ui.font_text.setCurrentFont('楷体')
        self.ui.fontsize_value.setValue(15)
        self.setting_changed.emit()

    def closeEvent(self, event: PySide2.QtGui.QCloseEvent) -> None:
        event.ignore()


if __name__ == '__main__':
    app = QApplication([])
    # setting = SettingWidget()
    # setting.ui.show()
    from my_set import Ui_Setting

    test = QWidget()
    test.ui = Ui_Setting()
    test.ui.setupUi(test)
    test.show()
    print(test.get_setting_data())
    app.exec_()
