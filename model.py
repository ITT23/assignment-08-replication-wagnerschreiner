from matplotlib import pyplot as plt
import numpy as np
import os
import random

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# import a lot of things from keras:
# sequential model
from keras.models import Sequential

# layers
from keras.layers import Input, Dense, LSTM, GRU, BatchNormalization, Dropout

# loss function
from keras.metrics import categorical_crossentropy

# callback functions
from keras.callbacks import ReduceLROnPlateau, EarlyStopping

# convert data to categorial vector representation
from keras.utils import to_categorical, pad_sequences

# helper function for train/test split
from sklearn.model_selection import train_test_split

# import confusion matrix helper function
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# resample signal to n samples
from scipy.signal import resample

# XML parser
import xml.etree.ElementTree as ET

# encoding and normalizing data
from sklearn.preprocessing import LabelEncoder

from data_augmentation import Augmenter

NUM_POINTS = 50


class Model:

    def __init__(self):
        self.labels = []
        self.X_train, self.X_test, self.y_train, self.y_test = self.load_data()
        self.model = self.train_model()

    def load_data(self):
        data = []

        for root, subdirs, files in os.walk('dataset'):
            if 'ipynb_checkpoint' in root:
                continue
            
            if len(files) > 0:
                for f in files:
                    if '.xml' in f:
                        fname = f.split('.')[0]
                        label = fname[:-2]
                        
                        xml_root = ET.parse(f'{root}/{f}').getroot()
                        
                        points = []
                        for element in xml_root.findall('Point'):
                            x = element.get('X')
                            y = element.get('Y')
                            points.append([x, y])
                            
                        points = np.array(points, dtype=float)
                        
                        data.append((label, points))


        augmenter = Augmenter(gestures=data)
        training_set = augmenter.get_avc_set()


        self.labels = [sample[0] for sample in training_set]
        print(set(self.labels))

        self.encoder = LabelEncoder()
        labels_encoded = self.encoder.fit_transform(self.labels)

        print(set(labels_encoded))
        y = to_categorical(labels_encoded)
        print(len(y[0]))

        sequences = [sample[1] for sample in training_set]
        sequences = pad_sequences(
            sequences, padding="pre", dtype='float32'
        )
        X = np.array(sequences)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

        return X_train, X_test, y_train, y_test


    def train_model(self):
        # Define the model
        model = Sequential()

            # add LSTM layer
            # input shape is (length of an individual sample, dimensions of the sample)
            # in our case: two dimensions, as we have X and Y coordinates
        model.add(LSTM(96))

            # add dense layer to do machine learning magic
        #model.add(BatchNormalization())
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
            # here, you can add more layers and maybe a dropout for better performance

            # softmax layer for classification
        model.add(Dense(len(set(self.labels)), activation='softmax'))

            # Compile the model
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=0.001)
        stop_early = EarlyStopping(monitor='val_loss', patience=3)
            
            # Train the model
        history = model.fit(
            self.X_train,
            self.y_train,
            epochs=30,
            batch_size=512,
            validation_data=(self.X_test, self.y_test),
            verbose=1,
            callbacks=[reduce_lr, stop_early]
        )

        return model


    def predict_gesture(self, gesture):
        # gesture = pad_sequences(
        #     gesture, padding="pre", dtype='float32'
        # )
        prediction = self.model.predict(np.array([gesture]))
        print(prediction)
        prediction = np.argmax(prediction)
        prediction_label = self.encoder.inverse_transform(np.array([prediction]))[0]
        print(prediction_label)
        return prediction_label