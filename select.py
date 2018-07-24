from openpyxl import Workbook, load_workbook
import os
import glob
import json

#directories
FIGRAM_PATH = '/media/mjia/Data/CNN-fMRI/FIGRIM/SCENES_700x700'
CROPPED_SUN_PATH = '/media/mjia/Data/CNN-fMRI/cropped'
TARGET_PATH = '/media/mjia/Data/CNN-fMRI/Pool'
if os.path.isdir(TARGET_PATH):
    os.popen("rm -r -f" + TARGET_PATH)
    os.popen("mkdir " + TARGET_PATH)
else:
    os.popen("mkdir " + TARGET_PATH)
XLSX_FILE = 'RankSUNDatabase.xlsx'

#: experimental setup constants
NUMBER_OF_PARTICIPANTS = 50
NUMBER_OF_UNIQUE_RUNS = 8
NUMBER_OF_SHARED_RUNS = 1
UNIQUE_IMAGES_PER_UNIQUE_RUN = 56
SHARED_IMAGES_PER_UNIQUE_RUN = 8
SHARED_IMAGES_PER_SHARED_RUN = 64

NUMBER_REQUIRED_OF_PARTICIPANTS = NUMBER_OF_UNIQUE_RUNS * UNIQUE_IMAGES_PER_UNIQUE_RUN

#the records
global_count = 0
subject_level_count = 0
residual_count = 0
selected_classes = []

#select from Figram
for dir, subdirs, files in os.walk(FIGRAM_PATH):
    for class_label in subdirs:
        all_files = glob.glob('{}*.jpg'.format(FIGRAM_PATH+os.sep+class_label+os.sep), recursive=True)
        # if the class contains less than 51 image, do not select it
        if len(all_files) <= NUMBER_OF_PARTICIPANTS:
            continue
        global_count += len(all_files)
        subject_level_count += len(all_files)//NUMBER_OF_PARTICIPANTS
        residual_count += len(all_files)%NUMBER_OF_PARTICIPANTS
        selected_classes.append(class_label)

        class_label = class_label.replace(' ', '\ ')
        os.popen("cp -r {0} {1}".format(FIGRAM_PATH+os.sep+class_label, TARGET_PATH))
        print("add *" + class_label + "* to pool, current has " + str(global_count))

#select the class in RankSUNDatabase.xlsx
wb=load_workbook(XLSX_FILE)
first_sheet = wb.get_sheet_names()[0]
worksheet = wb.get_sheet_by_name(first_sheet)
for i in range(2, 89):
    class_label = worksheet["A"+str(i)].value.lower()
    #check if it's already selected
    if class_label not in selected_classes:
        all_files = glob.glob('{}*.jpg'.format(CROPPED_SUN_PATH + os.sep + class_label + os.sep), recursive=True)
        # if the class contains less than 51 image, do not select it
        if len(all_files) <= NUMBER_OF_PARTICIPANTS:
            continue
        global_count += len(all_files)
        subject_level_count += len(all_files)//NUMBER_OF_PARTICIPANTS
        residual_count += len(all_files)%NUMBER_OF_PARTICIPANTS
        selected_classes.append(class_label)

        class_label = class_label.replace(' ', '\ ')
        os.popen("cp -r {0} {1}".format(CROPPED_SUN_PATH + os.sep + class_label, TARGET_PATH))
        print("add *" + class_label + "* to pool, current has " + str(global_count))


#select the class in SUN
sorts = []
for dir, subdirs, files in os.walk(CROPPED_SUN_PATH):
    for class_label in subdirs:
        if class_label not in selected_classes:
            all_files = glob.glob('{}*.jpg'.format(CROPPED_SUN_PATH + os.sep + class_label + os.sep), recursive=True)
            if len(all_files) <= NUMBER_OF_PARTICIPANTS:
                continue
            sorts.append([class_label, len(all_files)])

sorts.sort(key=lambda a: a[1], reverse=True)
for iterm in sorts:
    class_label = iterm[0]
    length = iterm[1]
    global_count += length
    subject_level_count += length // NUMBER_OF_PARTICIPANTS
    residual_count += length % NUMBER_OF_PARTICIPANTS
    selected_classes.append(class_label)

    class_label = class_label.replace(' ', '\ ')
    os.popen("cp -r {0} {1}".format(CROPPED_SUN_PATH + os.sep + class_label, TARGET_PATH ))
    print("add *" + class_label + "* to pool, current has " + str(global_count))

    if subject_level_count >= NUMBER_REQUIRED_OF_PARTICIPANTS:
        break

with open('info.json', 'w') as outfile:
    json.dump(selected_classes, outfile)

print('done')