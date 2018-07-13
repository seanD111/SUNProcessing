from . import argparse

from . import SUNProcessing


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-S', '--SUN', help = '''Root directory of the SUN
		database.''')

	parser.add_argument('-F', '--FIGRIM', help = '''Root directory of the FIGRIM
		database.''')

	parser.add_argument('-l', '--log', help = '''Directory to write output log''')


	parser.add_argument('-x', '--xls', help = '''Path to xls file to append class information''')

	parser.add_argument('-c', '--crop', help = '''Directory to output cropped images''')

	args = vars(parser.parse_args())
	args = {k: v for k, v in args.items() if v}

	#: if the user has entered both the SUN and FIGRIM dataset locations
	if 'SUN' in args and 'FIGRIM' in  args:
		#: find all images in each database, along with images above threshold
		sun_processor = SUNProcessing.Processor(args['SUN'])
		figrim_processor = SUNProcessing.Processor(args['FIGRIM'])
		sun_processor.get_class_information()
		figrim_processor.get_class_information()

		#: merge the information of both datasets 
		sun_processor.merge(figrim_processor)
		
		if 'xls' in args:
			sun_processor.write_to_xls(args['xls'])
		if 'log' in args:
			sun_processor.print_class_information(args['log'])
		if 'crop' in args:
			sun_processor.crop_thresholded_images(args['crop'])

	else:
		print('Run SUNProcessing with -h to see possible arguments')	
