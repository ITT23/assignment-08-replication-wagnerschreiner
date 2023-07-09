import numpy as np
from scipy.signal import resample
import xml.etree.ElementTree as ET
import os
from sklearn.preprocessing import StandardScaler

def load_data(gestures):
    data = []
    labels = []

    for root, subdirs, files in os.walk('dataset/xml_logs'):
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
                    
                    scaler = StandardScaler()
                    points = scaler.fit_transform(points)
                    
                    resampled = resample(points, 64)
                    
                    if not label in labels and label in gestures:
                        data.append((label, resampled))
                        labels.append(label)

                    if len(labels) == len(gestures):
                        print("all files loaded successfully", len(data))
                        return data

    print("all files loaded successfully", len(data))

    return data


# add noise (uniform, gaussian, perlin noise)
def add_gaussian_noise(sequence):
    noise = np.random.normal(0, 0.08, sequence.shape) # the authors use sigma=0.08
    noise_seq = sequence + noise
    return noise_seq

# scaling
def scaling(sequence):
    centroid = np.mean(sequence)
    rnd = np.random.uniform(0.8, 1.2) 
    points = sequence - centroid
    scaled_seq = points * rnd
    scaled_seq += centroid
    return scaled_seq

# rotation

# shearing: results in stretching of the original trajectory along a line

# perspective change: rotating the trajectory around the x and y axes (adding 3rd dimension & multiplying points by the x and y rotation matrices)

# spatial resampling: generate list of distance intervals & using the list to sample points along the trajectory

# temporal resampling: list of intervals in time domain

# temporal jitter: special case of temporal resampling with varying intervals

# time stretching: duplicating random subset of points in a trajectory

# frame skipping: removal of some points from the trajectory

# bezier and spline deformation: finding reasonable control points, pertubing them and fitting the new points to a spline curve

# random erasing: replace some of the trajectory with values of 0