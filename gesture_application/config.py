'''
This module stores default value for application.

Most values taken from https://github.com/maslychm/gesture_augmentation/tree/main
'''
from enum import Enum

GAUSSIAN_NOISE_SIGMA = 0.8
SCALING_LOWER_BOUND = 0.8
SCALING_UPPER_BOUND = 1.2
SPATIAL_RESAMPLING_LOWER_BOUND = 5
PERSPECTIVE_CHANGE_MIN_ANGLE = -30
PERSPECTIVE_CHANGE_MAX_ANGLE = 30
ROTATION_MIN_ANGLE = -20
ROTATION_MAX_ANGLE = 20
SKIP_FRAME_CHANCE = 0.3
NUMBER_OF_SAMPLES = 300
MAX_EPOCHS = 30

WINDOW_WIDTH = 850
WINDOW_HEIGHT = 1000


class AugmentationPipelines(Enum):
    AVC = "AVC"
    SIMPLE = "Simple Chain"
    GAUSSIAN = "Gaussian"
