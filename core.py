from . import glob
from . import os
from . import collections
from . import Image

PIXEL_WIDTH_THRESHOLD = 700
PIXEL_HEIGHT_THRESHOLD = 700

def image_threshold_function(image_shape):
	if image_shape[1] >= PIXEL_HEIGHT_THRESHOLD and image_shape[0] >= PIXEL_WIDTH_THRESHOLD:
		return True
	else:
		return False

def get_class_information(path):
	database_path = os.path.abspath(path);	
	database_root_name = database_path.split(os.sep)[-1]
	classes_summary = collections.OrderedDict()
	classes_meeting_threshold = collections.OrderedDict()


	all_files = glob.iglob('{0}{1}**{1}*.jpg'.format(database_path, os.sep), recursive = True)

	for image_file in all_files:
		# cv2.imshow('image',image)
		# print(image.shape)
		# cv2.waitKey(0)
		dir_list = image_file.split(os.sep) 
		information = dir_list[-3:]
		if(len(information[0])==1):
			information = information[-2:]
		else:
			information = [' '.join(information[0:2]), information[-1]] 

		image_class = information[0]
		image_name = information[1]
		image_location = image_file
		classes_summary.setdefault(image_class, []).append({'id': image_name, database_root_name: image_location})

		with Image.open(image_file) as image:
			if(image_threshold_function(image.size)):
				classes_meeting_threshold.setdefault(image_class, []).append({'id': image_name, database_root_name: image_location})


	for image_class in classes_summary:
		print('{} total count: {}. Meeting threshold: {}'.format(image_class, 
			len(classes_summary.get(image_class, [])), 
			len(classes_meeting_threshold.get(image_class, []))
		))


