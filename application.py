import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from model import Model

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(800, 800)
        self.canvas.fill(Qt.white)
        self.label.setPixmap(self.canvas)
        self.setCentralWidget(self.label)

        self.toolButton = QtWidgets.QToolButton(self.label)
        self.toolButton.setGeometry(QtCore.QRect(700, 50, 41, 41))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("undo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon)
        self.toolButton.clicked.connect(self.undo)

        self.line = []
        self.last_x, self.last_y = None, None

    
    def undo(self):
        painter = QtGui.QPainter(self.label.pixmap())
        p = painter.pen()
        p.setWidth(10)
        p.setColor(QtGui.QColor("#fff"))
        painter.setPen(p)
        for point in self.line:
            if self.last_x is None:
                self.last_x, self.last_y = point
            else:    
                painter.drawLine(self.last_x, self.last_y, point[0], point[1])
                self.last_x, self.last_y = point
        painter.end()
        self.update()

        # set everything to default again
        self.line = []
        self.last_x = None
        self.last_y = None
        

    def mouseMoveEvent(self, e):
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.

        self.painter = QtGui.QPainter(self.label.pixmap())
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

    def mouseReleaseEvent(self, e):
        prediction = recognizer.predict_gesture(self.line)
        self.last_x = None
        self.last_y = None

# train model
recognizer = Model()

# application
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()