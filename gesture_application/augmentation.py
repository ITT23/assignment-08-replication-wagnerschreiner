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
                counter += 1
                self.progress.emit(counter)
        self.finished.emit(training_set)

    def avc_transformation(self, sequence):
        noise_seq = self.add_gaussian_noise(sequence)
        skipped_seq = self.skip_frames(noise_seq)
        resampled_seq = self.spatial_resampling(skipped_seq)
        persp_seq = self.perspective_change(resampled_seq)
        rotated_seq = self.rotate(persp_seq)
        scaled_seq = self.scaling(rotated_seq)
        return scaled_seq

    def simple_transformation(self, sequence):
        rotated_seq = self.rotate(sequence)
        scaled_seq = self.scaling(rotated_seq)
        gaussian_seq = self.add_gaussian_noise(scaled_seq)
        return gaussian_seq

    # add noise (uniform, gaussian, perlin noise)
    def add_gaussian_noise(self, sequence):
        # the authors use sigma=0.08
        noise = np.random.normal(
            0, config.GAUSSIAN_NOISE_SIGMA, sequence.shape)
        noise_seq = sequence + noise
        return noise_seq

    # scaling
    def scaling(self, sequence):
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

    # spatial resampling: generate list of distance intervals & using the list to sample points along the trajectory
    def spatial_resampling(self, sequence):
        resampled_seq = resample(sequence, np.random.randint(
            config.SPATIAL_RESAMPLING_LOWER_BOUND, len(sequence)*2))
        return np.array(resampled_seq)

    # perspective change: rotating the trajectory around the x and y axes (adding 3rd dimension & multiplying points by the x and y rotation matrices)
    def perspective_change(self, sequence):
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

    # frame skipping: removal of some points from the trajectory
    def skip_frames(self, sequence):
        skipped_seq = []
        for point in sequence:
            if np.random.uniform(low=0, high=1.0) >= config.SKIP_FRAME_CHANCE:
                skipped_seq.append(point)
        return np.asarray(skipped_seq)

    # rotation
    def rotate(self, sequence):
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

    # shearing: results in stretching of the original trajectory along a line

    # temporal resampling: list of intervals in time domain

    # temporal jitter: special case of temporal resampling with varying intervals

    # time stretching: duplicating random subset of points in a trajectory

    # bezier and spline deformation: finding reasonable control points, pertubing them and fitting the new points to a spline curve

    # random erasing: replace some of the trajectory with values of 0
