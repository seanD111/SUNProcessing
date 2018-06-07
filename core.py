from . import glob
from . import os
from . import collections
from . import json
from . import Image
from . import openpyxl

PIXEL_WIDTH_THRESHOLD = 700
PIXEL_HEIGHT_THRESHOLD = 700

def image_threshold_function(image_shape):
	if image_shape[1] >= PIXEL_HEIGHT_THRESHOLD and image_shape[0] >= PIXEL_WIDTH_THRESHOLD:
		return True
	else:
		return False

class Processor:
	def __init__(self, path):
		self.__path = os.path.abspath(path);	
		self.__root_name = self.__path.split(os.sep)[-1]
		self.all_classes = collections.OrderedDict()
		self.thresholded_classes = collections.OrderedDict()

	def get_class_information(self):

		all_files = glob.iglob('{0}{1}**{1}*.jpg'.format(self.__path, os.sep), recursive = True)

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

			image_class = information[0].replace('_', ' ')
			image_name = information[1]
			image_location = image_file
			self.all_classes.setdefault(image_class, []).append({'id': image_name, self.__root_name: image_location})

			with Image.open(image_file) as image:
				if(image_threshold_function(image.size)):
					self.thresholded_classes.setdefault(image_class, []).append({'id': image_name, self.__root_name: image_location})

	def print_class_information(self):
		with open('{}.txt'.format(self.__path), 'w') as outfile:
			for image_class in self.all_classes:
				outfile.write('{} meeting threshold: {}/{}\n'.format(image_class, 
					len(self.thresholded_classes.get(image_class, [])),
					len(self.all_classes.get(image_class, []))
				))

	def write_to_xls(self, worksheet_path):
		self.spreadsheet = os.path.abspath(worksheet_path)

		wb = openpyxl.load_workbook(self.spreadsheet)

		# grab the active worksheet
		ws = wb.active
		ws_classes = ws['A1':'A89']
		for ws_row in ws_classes:
			for ws_class in ws_row:
				print(ws_class.value)
				ws_class_name = ws_class.value.lower().strip()
				if ws_class_name in self.thresholded_classes:
					ws['C{}'.format(ws_class.row)].value = len(self.thresholded_classes[ws_class_name])

		wb.save(os.path.abspath(worksheet_path.replace('.', '_modified.')))




	


