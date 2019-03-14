from nilearn import image
from nilearn import datasets
from nilearn.input_data import NiftiLabelsMasker


atlas_dataset = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
atlas_filename = atlas_dataset.maps
labels = atlas_dataset.labels

print('Atlas ROIs are located in nifti image (4D) at: %s' %atlas_filename)  # 4D data

adhd_dataset=datasets.fetch_adhd(n_subjects=10, data_dir='F:\sample-data', url=None, resume=True, verbose=1)
keys=adhd_dataset.keys()
print(keys)
func_filenames=adhd_dataset.func
print(func_filenames[0])
confounds=adhd_dataset.confounds


masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, memory='nilearn_cache', verbose=5)

# Here we go from nifti files to the signal time series in a numpy
# array. Note how we give confounds to be regressed out during signal
# extraction
for filename, confound in zip(func_filenames, confounds):
    time_series = masker.fit_transform(filenames, confounds=confounds)

# for filename, confound in zip(func_filenames, confounds):
    # call transform from RegionExtractor object to extract timeseries signals
#  timeseries_each_subject = extractor.transform(filename, confounds=confound)