import config as config
import numpy as np
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt


class InputWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setup_UI()

        # Globals
        self.gestures = []
        self.line = []
        self.last_x, self.last_y = None, None

    def setup_UI(self):
        layout = QtWidgets.QGridLayout()

        self.input_label = QtWidgets.QLabel("Gesture Name:")
        self.gesture_name_input = QtWidgets.QLineEdit()
        self.input_label.setBuddy(self.gesture_name_input)

        self.canvas_wrapper = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(800, 800)
        self.canvas.fill(Qt.white)
        self.canvas_wrapper.setPixmap(self.canvas)
        self.canvas_wrapper.mouseMoveEvent = self.draw

        self.confirm_button = QtWidgets.QToolButton()
        confirm_icon = QtGui.QIcon()
        confirm_icon.addPixmap(QtGui.QPixmap(
            './gesture_application/assets/confirm.svg'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.confirm_button.setIcon(confirm_icon)
        self.confirm_button.clicked.connect(self.confirm)

        self.undo_button = QtWidgets.QToolButton()
        undo_icon = QtGui.QIcon()
        undo_icon.addPixmap(QtGui.QPixmap(
            './gesture_application/assets/undo.svg'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.undo_button.setIcon(undo_icon)
        self.undo_button.clicked.connect(self.clear_canvas)

        self.combo_box_label = QtWidgets.QLabel("Augmentation Pipeline:")
        self.combo_box = QtWidgets.QComboBox()
        for chain in config.AugmentationPipelines:
            self.combo_box.addItem(chain.value)
        self.combo_box_label.setBuddy(self.combo_box)

        self.start_button = QtWidgets.QPushButton(text='Start')

        self.gesture_list_view = QtWidgets.QListWidget()
        self.delete_button = QtWidgets.QToolButton()
        delete_icon = QtGui.QIcon()
        delete_icon.addPixmap(QtGui.QPixmap('./gesture_application/assets/delete.svg'),
                              QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_button.setIcon(delete_icon)
        self.delete_button.clicked.connect(self.delete_gesture)

        layout.addWidget(self.input_label, 0, 0)
        layout.addWidget(self.gesture_name_input, 0, 1)
        layout.addWidget(self.confirm_button, 0, 2)
        layout.addWidget(self.undo_button, 0, 3)
        layout.addWidget(self.canvas_wrapper, 1, 0, 1, 4)
        layout.addWidget(self.combo_box_label, 2, 0)
        layout.addWidget(self.combo_box, 2, 1)
        layout.addWidget(self.start_button, 2, 3)
        layout.addWidget(self.gesture_list_view, 3, 1)
        layout.addWidget(self.delete_button, 3, 3)

        self.setLayout(layout)

    def confirm(self):
        text = self.gesture_name_input.text()
        if text and self.line:
            self.gestures.append([text, np.array(self.line, dtype=float)])
            self.clear_canvas()
            self.update_gesture_list()

    def update_gesture_list(self):
        self.gesture_list_view.clear()
        for gesture in self.gestures:
            QtWidgets.QListWidgetItem(gesture[0], self.gesture_list_view)
        self.update()

    def delete_gesture(self):
        selected_item = self.gesture_list_view.currentRow()
        del self.gestures[selected_item]
        self.update_gesture_list()

    def clear_canvas(self):
        self.canvas_wrapper.clear()
        self.canvas_wrapper.setPixmap(self.canvas)
        self.update()
        self.line = []
        self.last_x = None
        self.last_y = None
        self.gesture_name_input.clear()

    def draw(self, e):
        if self.last_x is None:  # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return  # Ignore the first time.

        self.painter = QtGui.QPainter(self.canvas_wrapper.pixmap())
        p = self.painter.pen()
        p.setWidth(4)
        self.painter.setPen(p)
        self.painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        self.painter.end()
        self.update()

        # save drawn points
        self.line.append([e.x(), e.y()])

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, event):
        self.last_x = None
        self.last_y = None
