import cv2
import numpy as np
import glob
import json
import requests
import os
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--fetch', action="store_true", default="false")
args, unknown = parser.parse_known_args()
training = ""
BACKGROUND_COLOR = (0,0,0) #black

INPUT_JSON_FOLDER = 'input'
OUTPUT_COLOR_CORRECTED_FOLDER = 'output/images_color_corrected'
OUTPUT_LABELED_FOLDER = 'output/images_labeled'
OUTPUT_ORIGINAL_FOLDER = 'output/images_original'
paths=[]
BACKGROUND_COLOR = (0,0,0) #black
colorsByImage = dict()# 'nameOfFile' = ['#hexColor', '#hexColor','#hexColor', ...] contains a list of n colors, n=number of objects

# convert hexadecimal to RGB, and return a tuple
def hex_to_rgb(v):
    h = v.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


    
# create output directories if needed
for directory in [OUTPUT_COLOR_CORRECTED_FOLDER,OUTPUT_LABELED_FOLDER,OUTPUT_ORIGINAL_FOLDER]:
  try:
    os.makedirs(directory)
  except FileExistsError:
      pass # directory already exists



key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJja21tOWVpc3IyMXg4MDcxNHNsZGgwdWNkIiwib3JnYW5pemF0aW9uSWQiOiJja21tOWVpczdvMWRzMDc3MjhvZmIyNWhzIiwiYXBpS2V5SWQiOiJja21yanVhb3F6emM0MDc5MDJxZzk3eWo1IiwiaWF0IjoxNjE2ODM4NDA2LCJleHAiOjIyNDc5OTA0MDZ9.RmY5u0gWbfbgPEDsc_66a7_aeraDe5gPpFpm-iVDWlU"
if args.fetch:
    for path in glob.iglob(os.path.join(INPUT_JSON_FOLDER,'*.json')):
        with open(path) as json_file:
            data = json.load(json_file)
            print("Downloading the labels and the original files")
            printProgressBar(0, 100, prefix = 'Progress:', suffix = 'Complete', length = 50)
            for i in range(len(data)):
                printProgressBar(i + 1, len(data), prefix = 'Progress:', suffix = 'Complete', length = 50)
                filename = data[i]['External ID']
                orig_url = data[i]['Labeled Data']
                aux = [x for x in filename.split('.') if x.strip()]
                try:
                    paths.append(aux[0])# name of the file without the .png
                    os.mkdir(os.path.join(OUTPUT_LABELED_FOLDER, str(aux[0])))#create folder with name of filename
                except OSError:
                    pass
                colorsByImage[aux[0]]=[]
                for h in range(len(data[i]['Label']['objects'])):
                    try:
                        url = data[i]['Label']['objects'][h]['instanceURI']
                        colorsByImage[aux[0]].append(data[i]['Label']['objects'][h]['color'])
                        #print(url)
                        if "&token=" in url:
                            url = "".join(url.split("&token=")[:-1])
                            url = url+'&token='+key
                        elif "?token=" in url:
                            url = "".join(url.split("?token=")[:-1])
                            url = url+'?token='+key
                        res_label = requests.get(url)
                        res_label.raise_for_status()
                        open(os.path.join(OUTPUT_LABELED_FOLDER, str(aux[0]), str(h)+"."+"png"), 'wb').write(res_label.content)

                        if "&token=" in orig_url:
                            orig_url = "".join(orig_url.split("&token=")[:-1])
                            orig_url = orig_url+'&token='+key
                        elif "?token=" in orig_url:
                            orig_url = "".join(orig_url.split("?token=")[:-1])
                            orig_url = orig_url+'?token='+key
                        res_orig = requests.get(orig_url)
                        res_orig.raise_for_status()
                        open(os.path.join(OUTPUT_ORIGINAL_FOLDER,filename), 'wb').write(res_orig.content)
                    except :
                        pass

print("\nGenerating the labels corrected")
printProgressBar(0, 100, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i in range(len(paths)):
    printProgressBar((i+1), len(paths), prefix = 'Progress:', suffix = 'Complete', length = 50)
    tifCounter = len(glob.glob1(str(os.path.join(OUTPUT_LABELED_FOLDER, str(paths[i]))),"*.png"))
    filename = 'labeled_'+paths[i]+".png"
    input_line = os.path.join('training',OUTPUT_ORIGINAL_FOLDER, str(paths[i])+".png")
    output_line = os.path.join('training',OUTPUT_COLOR_CORRECTED_FOLDER,filename)
    aux = cv2.imread("")
    for path in glob.iglob(os.path.join(OUTPUT_LABELED_FOLDER, str(paths[i]),'*.png')):
        #print(input_line)
        img = cv2.imread(path)
    
        # Mask image to only select white
        white=np.array([200,200,200])
        mask=cv2.inRange(img,white,np.array([255,255,255]))
        #mask_inv = [not m for m in mask]

        nameOfLabelledFile = [x for x in str(path).split('/') if x.strip()]
        count = int([x for x in str(nameOfLabelledFile[-1]).split('.') if x.strip()][0])#example/1.png -> count = 1

        # Change image colors
        img[mask==0] = BACKGROUND_COLOR
        img[mask>0] = hex_to_rgb(colorsByImage[paths[i]][count])
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)#convert rgb to bgr -> opencv

        path = path.split('/')[-1]

        if aux is None:
            added_image = img
        else:
            added_image += img

        aux = added_image

    training += input_line + ' ' + output_line + '\n'
    cv2.imwrite(os.path.join(OUTPUT_COLOR_CORRECTED_FOLDER,filename), added_image)

print("\nCompleted!")
# write input and output file paths to file for training
with open(os.path.join("output","training.txt"), "w+") as training_file:
    training_file.write(training)
