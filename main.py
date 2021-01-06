#!/usr/bin/env python3

import cv2
import numpy as np
import glob
import json
import requests
import os

training = ""

# define custom colors for segmented images
ROAD_COLOR = (255,255,255) #white
BACKGROUND_COLOR = (0,0,0) #black

INPUT_JSON_FOLDER = 'input'
OUTPUT_COLOR_CORRECTED_FOLDER = 'output/images_color_corrected'
OUTPUT_LABELED_FOLDER = 'output/images_labeled'
OUTPUT_ORIGINAL_FOLDER = 'output/images_original'

# create output directories if needed
for directory in [OUTPUT_COLOR_CORRECTED_FOLDER,OUTPUT_LABELED_FOLDER,OUTPUT_ORIGINAL_FOLDER]:
  try:
    os.makedirs(directory)
  except FileExistsError:
      pass # directory already exists


key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjazJxNnpyNGNpODczMDgzODgydzBtMzI5Iiwib3JnYW5pemF0aW9uSWQiOiJjazJxNnpyM25pODZ4MDgzOHF4MnB2cW9nIiwiYXBpS2V5SWQiOiJja2psc3VjdmZoN2o4MDg5MmhxbHYxdzVyIiwiaWF0IjoxNjA5OTYwMzgxLCJleHAiOjIyNDExMTIzODF9.B-nk_NVBo_KxMKlbbf-EIh0dpY8bvVxjqFpMCBCGaUk"

# for path in glob.iglob(os.path.join(INPUT_JSON_FOLDER,'*.json')):
#     with open(path) as json_file:
#         data = json.load(json_file)
#         for i in range(len(data)):
#             try:
#               filename = data[i]['External ID']
#               orig_url = data[i]['Labeled Data']
#               url = data[i]['Label']['objects'][0]['instanceURI']
#               #print(url)
#               if "&token=" in url:
#                   url = "".join(url.split("&token=")[:-1])
#                   url = url+'&token='+key
#               elif "?token=" in url:
#                   url = "".join(url.split("?token=")[:-1])
#                   url = url+'?token='+key
#               res_label = requests.get(url)
#               res_label.raise_for_status()
#               open(os.path.join(OUTPUT_LABELED_FOLDER, filename), 'wb').write(res_label.content)
#
#               if "&token=" in orig_url:
#                   orig_url = "".join(orig_url.split("&token=")[:-1])
#                   orig_url = orig_url+'&token='+key
#               elif "?token=" in orig_url:
#                   orig_url = "".join(orig_url.split("?token=")[:-1])
#                   orig_url = orig_url+'?token='+key
#               res_orig = requests.get(orig_url)
#               res_orig.raise_for_status()
#               open(os.path.join(OUTPUT_ORIGINAL_FOLDER,filename), 'wb').write(res_orig.content)

for path in glob.iglob(os.path.join(OUTPUT_LABELED_FOLDER,'*.png')):
              filename = 'labeled_'+path.split("/")[-1]
              input_line = os.path.join('training',OUTPUT_ORIGINAL_FOLDER,filename)
              print(input_line)

              img = cv2.imread(path)

              # Mask image to only select white
              white=np.array([200,200,200])
              mask=cv2.inRange(img,white,np.array([255,255,255]))
              #mask_inv = [not m for m in mask]

              # Change image colors
              img[mask==0] = BACKGROUND_COLOR
              img[mask>0] = ROAD_COLOR

              path = path.split('/')[-1]
              cv2.imwrite(os.path.join(OUTPUT_COLOR_CORRECTED_FOLDER,filename),img)
              output_line = os.path.join('training',OUTPUT_COLOR_CORRECTED_FOLDER,filename)
              print(output_line)

              training += input_line + ' ' + output_line + '\n'

# write input and output file paths to file for training
with open(os.path.join("output","training.txt"), "w+") as training_file:
    training_file.write(training)
