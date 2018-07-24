import gist
import json
import glob
import os
import numpy
import h5py
import collections
from PIL import Image
from sklearn.decomposition import PCA
from Gist_Histogram import Subject

def which_bin(edges, gist_reduced):
    index = [None] * DIM_REDUCE_TO
    for i in range(DIM_REDUCE_TO):
        for j in range(NUMBER_OF_BIN):
            if edges[i][0][j] < gist_reduced[i] and edges[i][0][j+1] > gist_reduced[i]:
                break
        index[i] = [i, j]
    template = numpy.zeros(shape=(DIM_REDUCE_TO, NUMBER_OF_BIN))
    for iterm in index:
        template[iterm[0], iterm[1]] = 1
    return index, template

#: experimental setup constants
NUMBER_OF_PARTICIPANTS = 50
NUMBER_OF_UNIQUE_RUNS = 8
NUMBER_OF_SHARED_RUNS = 1
UNIQUE_IMAGES_PER_UNIQUE_RUN = 56
SHARED_IMAGES_PER_UNIQUE_RUN = 8
SHARED_IMAGES_PER_SHARED_RUN = 64

DIM_REDUCE_TO = 10
NUMBER_OF_BIN = 10
POOL_PATH = '/media/mjia/Data/CNN-fMRI/Pool_with_Gist'
TARGET_PATH = '/media/mjia/Data/CNN-fMRI/Final'

#create folders
'''os.popen('mkdir ' + TARGET_PATH)
for i in range(NUMBER_OF_PARTICIPANTS):
    os.popen('mkdir ' + TARGET_PATH + '/subject' + str(i))
    for dir, subdirs, files in os.walk(POOL_PATH):
        for class_label in subdirs:
            class_label = class_label.replace(' ', '\ ')
            os.popen('mkdir ' + TARGET_PATH + '/subject' + str(i) + '/' + class_label)'''

#PCA of GIST
h5f = h5py.File(POOL_PATH + "/GistFeatures_all.h5", 'r')
gist_all = h5f['GistFeatures'][:]
h5f.close()
pca = PCA(n_components=DIM_REDUCE_TO)
pca.fit(gist_all.transpose())
reduced_all = pca.transform(gist_all.transpose()) #24826 * 10
singular_values = pca.singular_values_
stacked_singular_values = []
for i in range(NUMBER_OF_BIN):
    stacked_singular_values.append(singular_values)
stacked_singular_values = numpy.stack(stacked_singular_values).transpose()


#global histogram
hist_all = numpy.empty(shape=(DIM_REDUCE_TO, NUMBER_OF_BIN)) #10 * 5
edges = [None] * DIM_REDUCE_TO # 10 * 6
for i in range(DIM_REDUCE_TO):
    hist_all[i, :], edges[i] = numpy.histogramdd(reduced_all[:, i], bins=NUMBER_OF_BIN)
hist_all_normalized = hist_all/(reduced_all.size)

#initialize subjects' histogram
subjects = []
for i in range(NUMBER_OF_PARTICIPANTS):
    a = Subject()
    subjects.append(a)
# go over all classes and assign to subjects
for dir, subdirs, files in os.walk(POOL_PATH):
    for class_label in subdirs:
        print(class_label)
        all_files = glob.glob('{}*.jpg'.format(POOL_PATH + os.sep + class_label + os.sep), recursive=True)
        each_participant_will_get = len(all_files)//NUMBER_OF_PARTICIPANTS
        # reset subjects' "this_class_assigned"
        for iterm in subjects:
            iterm.this_class_assigned = 0
        for current in all_files:
            h5f = h5py.File(current[:-3] + 'h5')
            current_gist = h5f['GistFeatures'][:]
            h5f.close()
            current_gist = numpy.expand_dims(current_gist, 0)
            current_gist_reduced = pca.transform(current_gist)
            index, template = which_bin(edges, numpy.squeeze(current_gist_reduced))

            # sort the subjects based on the difference of their hist with global hist (in this particulat bin)
            difference = []
            for i in range(NUMBER_OF_PARTICIPANTS):
                difference.append([i, subjects[i].difference(template*stacked_singular_values, hist_all_normalized)])
            #difference.sort(key=lambda a: a[1], reverse=True)
            # find the the most different one, subject to the prerequisite that its quota of this class isn't full
            for i in range(NUMBER_OF_PARTICIPANTS):
                if subjects[difference[i][0]].this_class_assigned < each_participant_will_get:
                    subjects[difference[i][0]].assign(current, template)
                    break
                else:
                    continue

            pass

# validation
sum_difference = 0
for iterm in subjects:
    # random selection get 3.45 (3.45/50 = 0.069), while this method get 0.653 (0.653 / 50 = 0.013)
    sum_difference += sum(sum(abs(stacked_singular_values*(hist_all_normalized - iterm.histgram_normalized))))

print(sum_difference)

# take action: copy images
'''for i in range(NUMBER_OF_PARTICIPANTS):
    subjects[i].assigned = subjects[i].assigned[:-1] # 449 - 1 = 448
    for file in subjects[i].assigned:
        file = file.replace(' ', '\ ')
        class_name = (file.split("/"))[-2]
        os.popen("mv " + file + " " + TARGET_PATH + "/subject" + str(i) + "/" + class_name)
        file = file[:-3] + 'h5'
        os.popen("mv " + file + " " + TARGET_PATH + "/subject" + str(i) + "/" + class_name)'''



print('done')





