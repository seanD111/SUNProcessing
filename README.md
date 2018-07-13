# SUNProcessing

Python module for combining/cropping of images in the SUN397 and FIGRIM datasets. Must be run as a module in command line, as demonstrated below:

py -m SUNProcessing -S "E:\seand\datasets\SUN397\SUN397" -F "E:\seand\datasets\SCENE
S_700x700\SCENES_700x700" -x "C:\Users\seand\Documents\GitHub\SUNProcessing\RankSUNDatabase_modified.xlsx" -c "./" -l ".
/test"

The -m parameter causes Python to run SUNProcessing as a module, running the main command line script in __main__.py
The -S parameter specifies the directory of the SUN397 database. This directory contains folders that correspond to the first letter of class names.
The -F parameter specifies the directory of the FIGRIM database. This directory contains folders corresponding to class names.
The -x parameter points to a .xlsx file, which contains class names in column A. The order of the classes determines the image selection order AFTER all FIGRIM images are selected.
The -c parameter specifies where the cropped images will be saved.
The -l parameter specifies where summary information will be saved. Summary information consists of two files:
	1) Text file showing how many images were in the databases vs how many met the cropping threshold
	2) json file of python dictionary. The dictionary summarizes the classes/images in the combined database, with the following structure:
		{
			"class_a": {
				"img_1.jpg": {
					"databaseA_img_location": "databaseA/path/to/img_1.jpg",
					"databaseB_img_location": "databaseB/path/to/img_1.jpg"
				},
				"img_2.jpg": {
					"databaseA_img_location": "databaseA/path/to/img_2.jpg",
					"databaseB_img_location": "databaseB/path/to/img_2.jpg"
				}
			},
			"class_b": {			
			}
			.
			.
			.
		}
