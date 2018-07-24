import gist
import json
import glob
import os
import numpy
import h5py
import collections
from PIL import Image

FIGRAM_DATABASE_KEY = "SCENES_700x700"
SUN_DATABASE_KEY = "SUN397"
CROPPED_DIR = "/home/mjia/Downloads/cropped"

#initial works
with open('/media/mjia/Data/CNN-fMRI/Summary_info.json') as f:
    data = json.load(f)

sum = 0
for key in data:
    sum += len(data[key])
#all images from figram will be selected
all_files = glob.glob( CROPPED_DIR + '/*/*.jpg', recursive = True)
gistf = numpy.ones((960, len(all_files)))
correspondingNames = []
filled = 0
for name in all_files:
    img = Image.open(name)
    current = gist.extract(numpy.array(img))
    gistf[:, filled] = current

    #save current
    h5f = h5py.File(name[:-3]+'h5', 'w')
    h5f.create_dataset('GistFeatures', data=current)
    h5f.close()

    correspondingNames.append(name)
    print(filled)
    filled += 1
    if filled == 50:
        break

h5f = h5py.File("GistFeatures_all.h5", 'w')
h5f.create_dataset('GistFeatures', data=gistf)
h5f.close()

print("done")
