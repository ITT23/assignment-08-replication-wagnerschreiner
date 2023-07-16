'''
This module acts as a PyQt widget manager.
'''
import sys

import config
from augmentation import Augmenter
from input_widget import InputWidget
from prediction_widget import PredictionWidget
from progress_widget import ProgressWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread

from model import Model


class ApplicationWindow(QtWidgets.QWidget):

    def __init__(self) -> None:
        '''
        Sets up PyQt UI elements.
        '''
        super(ApplicationWindow, self).__init__()
        self.input_view = InputWidget()
        self.prediction_view = PredictionWidget()
        self.progress_view = ProgressWidget()

        self.setFixedWidth(config.WINDOW_WIDTH)
        self.setFixedHeight(config.WINDOW_HEIGHT)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.input_view)
        self.stack.addWidget(self.prediction_view)
        self.stack.addWidget(self.progress_view)
        self.stack.setCurrentWidget(self.input_view)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.input_view.start_button.clicked.connect(self.start_training)
        self.prediction_view.canvas_wrapper.mouseReleaseEvent = self.handle_stop_drawing

    def start_training(self):
        '''
        Sets current widget to progress_view if enough gestures were recorded and starts model training.
        '''
        if len(self.input_view.gestures) > 1:
            print("Training started")
            self.stack.setCurrentWidget(self.progress_view)
            self.get_training_dataset()

    def get_training_dataset(self):
        '''
        Launches gesture augmentation in new PyQt QThread and adds Callback for progress.

        After https://realpython.com/python-pyqt-qthread/#using-qthread-vs-pythons-threading
        '''
        gestures = self.input_view.gestures
        self.progress_view.init_progress_bar(
            upper_bound=len(gestures)*config.NUMBER_OF_SAMPLES)
        self.dataset_thread = QThread()
        self.augmenter = Augmenter(gestures=gestures,
                                   augmentation_chain=self.input_view.combo_box.currentText())
        self.augmenter.moveToThread(self.dataset_thread)
        self.dataset_thread.started.connect(self.augmenter.run)
        self.augmenter.finished.connect(self.dataset_thread.quit)
        self.augmenter.finished.connect(self.augmenter.deleteLater)
        self.dataset_thread.finished.connect(
            self.dataset_thread.deleteLater)
        self.augmenter.progress.connect(self.report_augmentation_progress)
        self.dataset_thread.start()

        self.augmenter.finished.connect(self.train_model)

    def report_augmentation_progress(self, n):
        '''
        Callback method for gesture augmentation progress.
        '''
        self.progress_view.update_augmentation_progress(n)

    def train_model(self, training_set):
        '''
        Launches model training in PyQt QThread and adds Callback for progress.

        After https://realpython.com/python-pyqt-qthread/#using-qthread-vs-pythons-threading
        '''
        self.progress_view.init_progress_bar(upper_bound=config.MAX_EPOCHS)
        self.training_thread = QThread()
        self.predictor = Model(training_set=training_set)
        self.predictor.moveToThread(self.training_thread)
        self.training_thread.started.connect(self.predictor.run)
        self.predictor.finished.connect(self.training_thread.quit)
        self.predictor.finished.connect(self.predictor.deleteLater)
        self.training_thread.finished.connect(self.training_thread.deleteLater)
        self.predictor.progress.connect(self.report_training_progress)
        self.training_thread.start()

        self.training_thread.finished.connect(self.change_view_to_prediction)

    def change_view_to_prediction(self):
        '''
        Sets current widget to prediction_view after model training is finished.
        '''
        self.stack.setCurrentWidget(self.prediction_view)

    def report_training_progress(self, step: int):
        '''
        Callback method for model training progress.
        '''
        self.progress_view.update_training_progress(step)

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
