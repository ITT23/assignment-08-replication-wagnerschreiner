'''
This module contains PyQt UI elements to display the progress of data augmentation and RNN training.
'''
import config
from PyQt5 import QtCore, QtWidgets


class ProgressWidget(QtWidgets.QWidget):
    def __init__(self,) -> None:
        super().__init__()
        self.setup_UI()
        self.augmentation = True

    def setup_UI(self):
        '''
        Initializes UI elements.
        '''
        layout = QtWidgets.QVBoxLayout()

        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch(1)

        self.setLayout(layout)

    def update_training_progress(self, n):
        '''
        Updates progress bar whenever RNN training progresses.
        '''
        self.progress_label.setText(f'Epoch {n} of {config.MAX_EPOCHS}')
        self.progress_bar.setValue(n)
        self.update()

    def update_augmentation_progress(self, n):
        '''
        Updates progress bar whenever data augmentation progresses.
        '''
        self.progress_bar.setValue(n)
        self.update()

    def init_progress_bar(self, upper_bound):
        '''
        Changes range of progress bar to use same widget for augmentation and RNN training.
        '''
        self.progress_label.setText('Generating training set...')
        self.progress_bar.setRange(0, upper_bound)
