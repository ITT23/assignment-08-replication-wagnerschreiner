import os

import config as config
import numpy as np
from keras.callbacks import Callback, EarlyStopping, ReduceLROnPlateau
from keras.layers import GRU, LSTM, BatchNormalization, Dense, Dropout, Input
from keras.metrics import categorical_crossentropy
from keras.models import Sequential
from keras.utils import pad_sequences, to_categorical
from PyQt5.QtCore import QObject, pyqtSignal
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class Model(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, training_set):
        super().__init__()

        self.labels = []
        self.training_set = training_set

    def load_data(self):
        self.labels = [sample[0] for sample in self.training_set]
        print(set(self.labels))

        self.encoder = LabelEncoder()
        labels_encoded = self.encoder.fit_transform(self.labels)

        print(set(labels_encoded))
        y = to_categorical(labels_encoded)
        print(len(y[0]))

        sequences = [sample[1] for sample in self.training_set]
        sequences = pad_sequences(
            sequences, padding="pre", dtype='float32'
        )
        X = np.array(sequences)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)
        print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

        return X_train, X_test, y_train, y_test

    def run(self):
        self.X_train, self.X_test, self.y_train, self.y_test = self.load_data()
        # Define the model
        model = Sequential()

        # add LSTM layer
        # input shape is (length of an individual sample, dimensions of the sample)
        # in our case: two dimensions, as we have X and Y coordinates
        model.add(LSTM(96))

        # add dense layer to do machine learning magic
        # model.add(BatchNormalization())
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        # here, you can add more layers and maybe a dropout for better performance

        # softmax layer for classification
        model.add(Dense(len(set(self.labels)), activation='softmax'))

        # Compile the model
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam', metrics=['accuracy'])

        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss', factor=0.2, patience=2, min_lr=0.001)
        stop_early = EarlyStopping(monitor='val_loss', patience=3)

        # Train the model
        history = model.fit(
            self.X_train,
            self.y_train,
            epochs=config.MAX_EPOCHS,
            batch_size=512,
            validation_data=(self.X_test, self.y_test),
            verbose=1,
            callbacks=[reduce_lr, stop_early,
                       TrainingCallback(progress=self.progress)]
        )

        self.finished.emit()

        self.model = model

    def predict_gesture(self, gesture):
        prediction = self.model.predict(np.array([gesture]))
        prediction_index = np.argmax(prediction)
        prediction_label = self.encoder.inverse_transform(
            np.array([prediction_index]))[0]
        confidence = prediction[0][prediction_index]
        return confidence, prediction_label


class TrainingCallback(Callback):
    def __init__(self, progress):
        super().__init__()
        self.progress = progress

    def on_epoch_end(self, epoch, logs=None):
        self.progress.emit(epoch+1)
