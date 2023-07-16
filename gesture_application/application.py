import sys
from threading import Thread

from input_widget import InputWidget
from model_worker_thread import Model
from prediction_widget import PredictionWidget
from progress_widget import ProgressWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QWidget


class ApplicationWindow(QtWidgets.QWidget):

    def __init__(self) -> None:
        super(ApplicationWindow, self).__init__()
        self.input_view = InputWidget()
        self.prediction_view = PredictionWidget()
        self.progress_view = ProgressWidget()

        self.setMinimumWidth(850)
        self.setMinimumHeight(1000)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.input_view)
        self.stack.addWidget(self.prediction_view)
        self.stack.addWidget(self.progress_view)
        self.stack.setCurrentWidget(self.input_view)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.input_view.start_button.clicked.connect(self.start_training)
        self.prediction_view.canvas_wrapper.mouseReleaseEvent = self.handle_stop_drawing

    def start_training(self):
        if len(self.input_view.gestures) > 1:
            print("Training started")
            self.stack.setCurrentWidget(self.progress_view)
            self.train_model_qthread()
            # train_model_thread = Thread(target=self.train_model)
            # train_model_thread.start()
            # self.change_view_to_prediction()

    def train_model(self):
        self.predictor = Model(gestures=self.input_view.gestures,
                               augmentation_chain=self.input_view.combo_box.currentText())
        self.predictor.run()

    def train_model_qthread(self):

        # After https://realpython.com/python-pyqt-qthread/#using-qthread-vs-pythons-threading
        self.training_thread = QThread()
        self.predictor = Model(gestures=self.input_view.gestures,
                               augmentation_chain=self.input_view.combo_box.currentText())
        self.predictor.moveToThread(self.training_thread)
        self.training_thread.started.connect(self.predictor.run)
        self.predictor.finished.connect(self.training_thread.quit)
        self.predictor.finished.connect(self.predictor.deleteLater)
        self.training_thread.finished.connect(self.training_thread.deleteLater)
        self.predictor.progress.connect(self.report_progress)
        self.training_thread.start()

        self.training_thread.finished.connect(self.change_view_to_prediction)

    def change_view_to_prediction(self):
        self.stack.setCurrentWidget(self.prediction_view)

    def report_progress(self, n):
        self.progress_view.update_progress(n)

    def handle_stop_drawing(self, event):
        drawn_gesture = self.prediction_view.line
        confidence, prediction_label = self.predictor.predict_gesture(
            drawn_gesture)
        self.prediction_view.clear_canvas()
        self.prediction_view.show_prediction(
            confidence=(confidence*100), gesture=prediction_label)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec_())
