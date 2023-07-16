from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt


class PredictionWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setup_UI()

        self.line = []
        self.last_x, self.last_y = None, None

    def setup_UI(self):
        layout = QtWidgets.QVBoxLayout()

        self.prediction_label = QtWidgets.QLabel()
        self.prediction_label.setAlignment(Qt.AlignCenter)

        self.canvas_wrapper = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(800, 800)
        self.canvas.fill(Qt.white)
        self.canvas_wrapper.setPixmap(self.canvas)
        self.canvas_wrapper.mouseMoveEvent = self.draw

        layout.addWidget(self.prediction_label)
        layout.addWidget(self.canvas_wrapper)

        self.setLayout(layout)

    def clear_canvas(self):
        self.canvas_wrapper.clear()
        self.canvas_wrapper.setPixmap(self.canvas)
        self.update()

        # set everything to default again
        self.line = []
        self.last_x = None
        self.last_y = None

    def show_prediction(self, gesture, confidence):
        self.prediction_label.setText(
            f'Gesture is {gesture} ({round(confidence, 2)}%)')
        self.update()

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
