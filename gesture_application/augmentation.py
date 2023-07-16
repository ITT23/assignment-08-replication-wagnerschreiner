'''
This module augments a limited dataset of gestures to create a large dataset for RNN training.
'''
import config
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from scipy.signal import resample
from scipy.spatial.transform import Rotation as R


class Augmenter(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)

    def __init__(self, gestures, augmentation_chain) -> None:
        super().__init__()

        self.gestures = gestures
        self.augmentation_chain = augmentation_chain

    def run(self):
        '''
        Creates training set depending on selected augmentation pipeline.

        Returns training_set via PyQt signal
        '''
        training_set = []
        counter = 0
        for gesture in self.gestures:
            label = gesture[0]
            original_points = gesture[1]
            for i in range(config.NUMBER_OF_SAMPLES):
                if self.augmentation_chain == config.AugmentationPipelines.AVC.value:
                    training_set.append(
                        [label, self.avc_transformation(original_points)])
                if self.augmentation_chain == config.AugmentationPipelines.SIMPLE.value:
                    training_set.append(
                        [label, self.simple_transformation(original_points)])
                if self.augmentation_chain == config.AugmentationPipelines.GAUSSIAN.value:
                    training_set.append(
                        [label, self.add_gaussian_noise(original_points)])
                if self.augmentation_chain == config.AugmentationPipelines.NONE.value:
                    training_set.append(
                        [label, original_points])
                counter += 1
                self.progress.emit(counter)
        self.finished.emit(training_set)

    def avc_transformation(self, sequence):
        '''
        Augments sequence of points after AVC pipeline as described in https://www.eecs.ucf.edu/~jjl/pubs/Mykola-CHI23.pdf
        '''
        noise_seq = self.add_gaussian_noise(sequence)
        skipped_seq = self.skip_frames(noise_seq)
        resampled_seq = self.spatial_resampling(skipped_seq)
        persp_seq = self.perspective_change(resampled_seq)
        rotated_seq = self.rotate(persp_seq)
        scaled_seq = self.scaling(rotated_seq)
        return scaled_seq

    def simple_transformation(self, sequence):
        '''
        Augments sequence of points after Simple Chain pipeline as described in https://www.eecs.ucf.edu/~jjl/pubs/Mykola-CHI23.pdf
        '''
        rotated_seq = self.rotate(sequence)
        scaled_seq = self.scaling(rotated_seq)
        gaussian_seq = self.add_gaussian_noise(scaled_seq)
        return gaussian_seq

    def add_gaussian_noise(self, sequence):
        '''
        Adds noise to sequence of points
        '''
        noise = np.random.normal(
            0, config.GAUSSIAN_NOISE_SIGMA, sequence.shape)
        noise_seq = sequence + noise
        return noise_seq

    def scaling(self, sequence):
        '''
        Scales sequence of points in x and y direction by random amount
        '''
        centroid = np.mean(sequence)
        rnd_x = np.random.uniform(
            config.SCALING_LOWER_BOUND, config.SCALING_UPPER_BOUND)
        rnd_y = np.random.uniform(
            config.SCALING_LOWER_BOUND, config.SCALING_UPPER_BOUND)
        points = sequence - centroid
        scaled_seq = []
        for x, y in points:
            scaled_x = x*rnd_x
            scaled_y = y*rnd_y
            scaled_seq.append([scaled_x, scaled_y])
        scaled_seq += centroid
        return scaled_seq

    def spatial_resampling(self, sequence):
        '''
        Generates list of distance intervals and samples points along trajectory
        '''
        resampled_seq = resample(sequence, np.random.randint(
            config.SPATIAL_RESAMPLING_LOWER_BOUND, len(sequence)*2))
        return np.array(resampled_seq)

    def perspective_change(self, sequence):
        '''
        Rotates trajectory around x and y axes
        '''
        persp_seq = []
        centroid = np.mean(sequence)
        y_angle = np.random.randint(
            config.PERSPECTIVE_CHANGE_MIN_ANGLE, config.PERSPECTIVE_CHANGE_MAX_ANGLE)
        x_angle = np.random.randint(
            config.PERSPECTIVE_CHANGE_MIN_ANGLE, config.PERSPECTIVE_CHANGE_MAX_ANGLE)
        r = R.from_euler('yx', [y_angle, x_angle], degrees=True)
        sequence = sequence - centroid
        mat = r.as_matrix()
        for point in sequence:
            point = np.append(point, 1)
            new_point = np.array(mat @ point)
            persp_seq.append(new_point[:-1])
        persp_seq += centroid
        return persp_seq

    def skip_frames(self, sequence):
        '''
        Removes points from trajectory
        '''
        skipped_seq = []
        for point in sequence:
            if np.random.uniform(low=0, high=1.0) >= config.SKIP_FRAME_CHANCE:
                skipped_seq.append(point)
        return np.asarray(skipped_seq)

    def rotate(self, sequence):
        '''
        Rotates trajectory around centroid
        '''
        centroid = np.mean(sequence)
        points = sequence - centroid
        angle = np.random.randint(
            low=config.ROTATION_MIN_ANGLE, high=config.ROTATION_MAX_ANGLE)
        r = R.from_euler('z', angle, degrees=True)
        mat = r.as_matrix()
        points_transformed = []
        for p in points:
            p = np.append(p, 1)
            result = np.array(mat @ p)
            result /= result[2]
            points_transformed.append(result[:-1])
        points_transformed += centroid
        return points_transformed
