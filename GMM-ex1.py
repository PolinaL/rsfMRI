from nilearn import image
from nilearn import datasets
from nilearn import input_data
from nilearn import plotting
from nilearn.connectome import ConnectivityMeasure

import matplotlib.pyplot as plt
import numpy as np

def plot_matrices(matrices, matrix_kind):
    n_matrices = len(matrices)
    fig = plt.figure(figsize=(n_matrices * 4, 4))
    for n_subject, matrix in enumerate(matrices):
        plt.subplot(1, n_matrices, n_subject + 1)
        matrix = matrix.copy()  # avoid side effects
        # Set diagonal to zero, for better visualization
        np.fill_diagonal(matrix, 0)
        vmax = np.max(np.abs(matrix))
        title = '{0}, subject {1}'.format(matrix_kind, n_subject)
        plotting.plot_matrix(matrix, vmin=-vmax, vmax=vmax, cmap='RdBu_r',
                             title=title, figure=fig, colorbar=False)





###############################################################################
# load data
adhd_dataset=datasets.fetch_adhd(n_subjects=2, data_dir='F:\sample-data',
                                 url=None, resume=True, verbose=1)
print(adhd_dataset['description'])
keys=adhd_dataset.keys()
print(keys)
func_filenames=adhd_dataset.func
print(func_filenames[0])
confounds=adhd_dataset.confounds
###############################################################################

###############################################################################
# extract the coordinates of Power atlas
power = datasets.fetch_coords_power_2011()
print('Power atlas comes with {0}.'.format(power.keys()))
power_coords = np.vstack((power.rois['x'], power.rois['y'], power.rois['z'])).T
print('Stacked power coordinates in array of shape {0}.'.format(power_coords.shape))
###############################################################################

###############################################################################
# extract spheres around ROIs, then detrend, clean from counfounds, band-pass filter
# and standardized to 1 variance the timeseries.
subject_tms = []
spheres_masker = input_data.NiftiSpheresMasker(
    seeds=power_coords, smoothing_fwhm=4, radius=5.,detrend=True, standardize=True,
    low_pass=0.1, high_pass=0.01, t_r=2.5)


for filename, confound in zip(func_filenames, confounds):
    time_series = spheres_masker.fit_transform(filename, confounds=confound)
    subject_tms.append(time_series)
    # plt.plot(time_series)

###############################################################################

###############################################################################
# calculate ROI to ROI correlations
correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrices = correlation_measure.fit_transform(subject_tms)

# All individual coefficients are stacked in a unique 2D matrix.
print('Correlations of ADHD patients are stacked in an array of shape {0}'
      .format(correlation_matrices.shape))
plot_matrices(correlation_matrices[:2], 'correlation')
###############################################################################


