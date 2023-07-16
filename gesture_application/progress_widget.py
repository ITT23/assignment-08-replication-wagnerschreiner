from PyQt5 import QtCore, QtGui, QtWidgets


class ProgressWidget(QtWidgets.QWidget):
    def __init__(self,) -> None:
        super().__init__()
        self.setup_UI()

    def setup_UI(self):
        layout = QtWidgets.QVBoxLayout()

        self.progress_label = QtWidgets.QLabel('Training Model')
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 30)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def update_progress(self, n):
        self.progress_bar.setValue(n)
