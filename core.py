from . import glob
from . import os
from . import collections
from . import json
from . import Image
from . import openpyxl
from . import shutil
from . import random

## CONSTANTS ##

#: minimum width and height of images 
PIXEL_WIDTH_THRESHOLD = 700
PIXEL_HEIGHT_THRESHOLD = 700

#: experimental setup constants
NUMBER_OF_PARTICIPANTS = 50
NUMBER_OF_UNIQUE_RUNS = 8
NUMBER_OF_SHARED_RUNS = 1
UNIQUE_IMAGES_PER_UNIQUE_RUN = 56
SHARED_IMAGES_PER_UNIQUE_RUN = 8
SHARED_IMAGES_PER_SHARED_RUN = 64

CROPPED_IMAGE_LIMIT = NUMBER_OF_PARTICIPANTS * NUMBER_OF_UNIQUE_RUNS * UNIQUE_IMAGES_PER_UNIQUE_RUN + SHARED_IMAGES_PER_UNIQUE_RUN*NUMBER_OF_UNIQUE_RUNS + SHARED_IMAGES_PER_SHARED_RUN

#: the names of the database root directories
FIGRAM_DATABASE_KEY = "SCENES_700x700"
SUN_DATABASE_KEY = "SUN397"


def image_threshold_function(image_shape):
	"""Function used to filter images based on size
	Args:
		image_shape (:obj: 'list' of :obj: 'int'): width and height of image in pixels
	Returns:
		bool: True or false, depending on if image size meets required thresholds
	"""
	if image_shape[1] >= PIXEL_HEIGHT_THRESHOLD and image_shape[0] >= PIXEL_WIDTH_THRESHOLD:
		return True
	else:
		return False

class Processor:
	"""Class used to process and store database image information

	Args:
		path (str): string pointing to the root directory of 
			the database to process

	Attributes:
		__path (str): absolute path to the database directory
		__root_name (str): name of the database
		__spreadsheet (str): path to spreadsheet containing the order of classes
		all_classes (dict): dictionary holding information relating
			to all images in this database
		thresholded_classes (dict): dictionary holding information relating to 
			images in this database that satisfy the specified threshold function
		all_classes_merged (dict): dictionary holding information relating to all 
			images in this Processor and another merged Processor
		all_classes_merged (dict): dictionary holding information relating to thresholded 
			images in this Processor and another merged Processor
		xls_classes (list of str): ordered list of image classes to start 
			image selection
		
	"""
	def __init__(self, path):
		self.__path = os.path.abspath(path);	
		self.__root_name = self.__path.split(os.sep)[-1]
		self.all_classes = {self.__root_name: collections.OrderedDict()}
		self.thresholded_classes = {self.__root_name: collections.OrderedDict()}

	def db_name(self):
		return self.__root_name

	def get_all_class_keys(self):
		return list(self.all_classes[self.db_name()].keys())

	def get_all_image_keys_by_class(self, img_class):
		return list(self.all_classes[self.db_name()].get(img_class, {}).keys())

	def get_thresholded_class_keys(self):
		return list(self.thresholded_classes[self.db_name()].keys())

	def get_thresholded_image_keys_by_class(self, img_class):
		return list(self.thresholded_classes[self.db_name()].get(img_class, {}).keys())

	"""Fetches all image information and saves it to all_classes and thresholded_classes
		Dictionaries
	"""
	def get_class_information(self):
		#: find all jpg files
		all_files = glob.glob('{0}{1}**{1}*.jpg'.format(self.__path, os.sep), recursive = True)

		#: find the highest level path of all images
		common_path = os.path.commonpath(all_files)
		print(common_path)

		#: for each image path in the list
		# change  'all_files' to 'all_files[:3000]' to limit to 3000 images
		for image_file in all_files:
			#: put the images' relevant directory information in a list
			rel_path = os.path.relpath(image_file, common_path)			 
			dir_list = rel_path.split(os.sep) 

			information = dir_list
			#: if the first element only has one character, as is the case
			# for SUN397 classes
			if(len(information[0])==1):
				#: ignore the first element
				information = information[1:]
			#: join strings up until the image name to obtain class name
			#This is specifically for 'outdoor' and 'interior' classes
			information = [' '.join(information[0:-1]), information[-1]] 

			image_class = information[0].replace('_', ' ')
			image_name = information[1]
			image_location = image_file

			#: with the image name as a key, set its value to be the location of
			#the image on the computer
			self.all_classes[self.db_name()].setdefault(image_class, {})[image_name] = {self.db_name(): image_location}

			#: open the image and add it to the thresholded dictionary if it
			#meets the threshold
			with Image.open(image_file) as image:
				if(image_threshold_function(image.size)):
					self.thresholded_classes[self.db_name()].setdefault(image_class, {})[image_name] = {self.db_name(): image_location}

	"""Writes information about this Processor to file
	Arguments:
		path (str): path to write text and json file
	"""
	def print_class_information(self, path):
		total_count_meeting_threshold = 0
		total_count = 0
		with open('{}.txt'.format(os.path.abspath(path)), 'w') as outfile:
			for image_class in self.all_classes_merged:
				total_count_meeting_threshold += len(self.thresholded_classes_merged.get(image_class, []))
				total_count += len(self.all_classes_merged.get(image_class, []))
				outfile.write('{} meeting threshold: {}/{}\n'.format(image_class, 
					len(self.thresholded_classes_merged.get(image_class, [])),
					len(self.all_classes_merged.get(image_class, []))
				))
			outfile.write('TOTAL: {}/{}'.format(total_count_meeting_threshold,total_count))

		with open('{}.json'.format(os.path.abspath(path)), 'w') as outfile:
			json.dump(self.thresholded_classes[self.db_name()], outfile)

	"""Reads classes from spreadsheet, and updates information inside it
	Arguments:
		worksheet_path (str): path to worksheet
	"""
	def write_to_xls(self, worksheet_path):
		self.__spreadsheet = os.path.abspath(worksheet_path)
		self.xls_classes = []
		wb = openpyxl.load_workbook(self.__spreadsheet)

		# grab the active worksheet
		ws = wb.active
		ws_classes = ws['A2':'A89']
		for ws_row in ws_classes:
			for ws_class in ws_row:
				ws_class_name = ws_class.value.lower().strip()
				self.xls_classes.append(ws_class_name)
				if ws_class_name in self.thresholded_classes[self.db_name()]:
					ws['C{}'.format(ws_class.row)].value = len(self.thresholded_classes[self.db_name()][ws_class_name])

		wb.save(os.path.abspath(worksheet_path.replace('.', '_modified.')))


	"""Merges another Processor with self
	Arguments:
		other (Processor): other Processor to merge
	"""
	def merge(self, other):
		self.all_classes[other.db_name()] = other.all_classes[other.db_name()]
		self.thresholded_classes[other.db_name()] = other.thresholded_classes[other.db_name()]
		self.all_classes_merged = collections.OrderedDict()
		self.thresholded_classes_merged = collections.OrderedDict()
		all_class_keys = collections.OrderedDict.fromkeys([*self.get_all_class_keys(), *other.get_all_class_keys()])
		thresholded_class_keys = collections.OrderedDict.fromkeys([*self.get_thresholded_class_keys(), *other.get_thresholded_class_keys()])

		for img_class in all_class_keys:
			class_img_keys = collections.OrderedDict.fromkeys([*self.get_all_image_keys_by_class(img_class), *other.get_all_image_keys_by_class(img_class)])
			self.all_classes_merged.setdefault(img_class, {})
			for img_key in class_img_keys:
				merged_dict = dict(self.all_classes[self.db_name()].get(img_class, {}).get(img_key, {}))
				merged_dict.update(other.all_classes[other.db_name()].get(img_class, {}).get(img_key, {}))			
				self.all_classes_merged[img_class][img_key]= merged_dict

		for img_class in thresholded_class_keys:
			class_img_keys = collections.OrderedDict.fromkeys([*self.get_thresholded_image_keys_by_class(img_class),*other.get_thresholded_image_keys_by_class(img_class)])
			self.thresholded_classes_merged.setdefault(img_class, {})
			for img_key in class_img_keys:
				merged_dict = dict(self.thresholded_classes[self.db_name()].get(img_class, {}).get(img_key, {}))
				merged_dict.update(other.thresholded_classes[other.db_name()].get(img_class, {}).get(img_key, {}))
				self.thresholded_classes_merged[img_class][img_key]= merged_dict

	def crop_thresholded_images(self, out_root):
		out_images = os.path.abspath(os.path.join(out_root, 'cropped'))


		key_list = [*list(self.thresholded_classes[FIGRAM_DATABASE_KEY].keys()),
			*sorted( list(self.thresholded_classes_merged.keys()), 
				key = lambda ckey: len(list(self.thresholded_classes_merged[ckey].keys())),
				reverse = True
			)
		]
		class_order_descending = list(collections.OrderedDict.fromkeys(key_list))
		cropped_image_count = 0 

		for img_class in class_order_descending:
			if(len(self.thresholded_classes_merged[img_class].keys())>(NUMBER_OF_PARTICIPANTS+NUMBER_OF_UNIQUE_RUNS)):
				for img_name in self.thresholded_classes_merged[img_class]:
					outpath = os.path.abspath(os.path.join(out_images, img_class))
					if not os.path.exists(outpath):
						os.makedirs(outpath)

					if FIGRAM_DATABASE_KEY in self.thresholded_classes_merged[img_class][img_name]:
						shutil.copy(self.thresholded_classes_merged[img_class][img_name][FIGRAM_DATABASE_KEY], 
							outpath						
						)
					elif SUN_DATABASE_KEY in self.thresholded_classes_merged[img_class][img_name]:
						with Image.open(self.thresholded_classes_merged[img_class][img_name][SUN_DATABASE_KEY]) as image:

							aspect = image.size[0]/image.size[1]
							resized =None
							if aspect >= 1:
								resized = image.resize((int(PIXEL_WIDTH_THRESHOLD*aspect), PIXEL_WIDTH_THRESHOLD))
							else:
								resized = image.resize((PIXEL_WIDTH_THRESHOLD, int(PIXEL_WIDTH_THRESHOLD/aspect)))

							extra_width = resized.size[0] - PIXEL_WIDTH_THRESHOLD
							extra_height = resized.size[1] - PIXEL_HEIGHT_THRESHOLD
							
							left = random.randrange(extra_width+1)
							top = random.randrange(extra_height+1)
							right = left + PIXEL_WIDTH_THRESHOLD
							bottom = top + PIXEL_HEIGHT_THRESHOLD

							cropped_img = resized.crop((left, top, right, bottom))

							cropped_img.convert('RGB').save(os.path.join(outpath, img_name))
							cropped_image_count = cropped_image_count + 1
				if cropped_image_count > CROPPED_IMAGE_LIMIT:
					break












	


