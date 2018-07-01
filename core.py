from . import glob
from . import os
from . import collections
from . import json
from . import Image
from . import openpyxl
from . import shutil
from . import random

PIXEL_WIDTH_THRESHOLD = 700
PIXEL_HEIGHT_THRESHOLD = 700
NUMBER_OF_PARTICIPANTS = 50
FIGRAM_DATABASE_KEY = "SCENES_700x700"
SUN_DATABASE_KEY = "SUN397"

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

		all_files = glob.glob('{0}{1}**{1}*.jpg'.format(self.__path, os.sep), recursive = True)
		common_path = os.path.commonpath(all_files)
		print(common_path)
		for image_file in all_files:
			rel_path = os.path.relpath(image_file, common_path)
			 
			dir_list = rel_path.split(os.sep) 

			information = dir_list
			if(len(information[0])==1):
				information = information[1:]
			information = [' '.join(information[0:-1]), information[-1]] 

			image_class = information[0].replace('_', ' ')
			image_name = information[1]
			image_location = image_file
			self.all_classes.setdefault(image_class, {})[image_name] = {self.__root_name: image_location}

			with Image.open(image_file) as image:
				if(image_threshold_function(image.size)):
					self.thresholded_classes.setdefault(image_class, {})[image_name] = {self.__root_name: image_location}

	def print_class_information(self, path):
		total_count_meeting_threshold = 0
		total_count = 0
		with open('{}.txt'.format(os.path.abspath(path)), 'w') as outfile:
			for image_class in self.all_classes:
				total_count_meeting_threshold += len(self.thresholded_classes.get(image_class, []))
				total_count += len(self.all_classes.get(image_class, []))
				outfile.write('{} meeting threshold: {}/{}\n'.format(image_class, 
					len(self.thresholded_classes.get(image_class, [])),
					len(self.all_classes.get(image_class, []))
				))
			outfile.write('TOTAL: {}/{}'.format(total_count_meeting_threshold,total_count))

		with open('{}.json'.format(os.path.abspath(path)), 'w') as outfile:
			json.dump(self.thresholded_classes, outfile)

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


	def merge(self, other):

		all_class_keys = collections.OrderedDict.fromkeys([*list(self.all_classes.keys()), *list(other.all_classes.keys())])
		thresholded_class_keys = collections.OrderedDict.fromkeys([*list(self.thresholded_classes.keys()), *list(other.thresholded_classes.keys())])

		for img_class in all_class_keys:
			class_img_keys = collections.OrderedDict.fromkeys([*list(self.all_classes.get(img_class, {}).keys()), *list(other.all_classes.get(img_class, {}).keys())])
			self.all_classes.setdefault(img_class, {})
			for img_key in class_img_keys:
				merged_dict = dict(self.all_classes.get(img_class, {}).get(img_key, {}))
				merged_dict.update(other.all_classes.get(img_class, {}).get(img_key, {}))			
				self.all_classes[img_class][img_key]= merged_dict

		for img_class in thresholded_class_keys:
			class_img_keys = collections.OrderedDict.fromkeys([
				*list(self.thresholded_classes.get(img_class, {}).keys()), 
				*list(other.thresholded_classes.get(img_class, {}).keys())
				])
			self.thresholded_classes.setdefault(img_class, {})
			for img_key in class_img_keys:
				merged_dict = 	dict(self.thresholded_classes.get(img_class, {}).get(img_key, {}))
				merged_dict.update(other.thresholded_classes.get(img_class, {}).get(img_key, {}))
				self.thresholded_classes[img_class][img_key]= merged_dict

	def crop_thresholded_images(self, out_root):
		out_images = os.path.abspath(os.path.join(out_root, 'cropped'))

		class_order_descending = sorted( list(self.thresholded_classes.keys()), 
			key = lambda ckey: len(list(self.thresholded_classes[ckey].keys())),
			reverse = True
		)

		for img_class in class_order_descending:

			for img_name in self.thresholded_classes[img_class]:
				outpath = os.path.abspath(os.path.join(out_images, img_class))
				if not os.path.exists(outpath):
					os.makedirs(outpath)

				if FIGRAM_DATABASE_KEY in self.thresholded_classes[img_class][img_name]:
					shutil.copy(self.thresholded_classes[img_class][img_name][FIGRAM_DATABASE_KEY], 
						outpath						
					)
				elif SUN_DATABASE_KEY in self.thresholded_classes[img_class][img_name]:
					with Image.open(self.thresholded_classes[img_class][img_name][SUN_DATABASE_KEY]) as image:
						extra_width = image.size[0] - PIXEL_WIDTH_THRESHOLD
						extra_height = image.size[1] - PIXEL_HEIGHT_THRESHOLD
						
						left = random.randrange(extra_width+1)
						top = random.randrange(extra_height+1)
						right = left + PIXEL_WIDTH_THRESHOLD
						bottom = top + PIXEL_HEIGHT_THRESHOLD

						cropped_img = image.crop((left, top, right, bottom))

						cropped_img.convert('RGB').save(os.path.join(outpath, img_name))












	


