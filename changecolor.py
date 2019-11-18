#!/usr/bin/env python3

import cv2
import numpy as np
import glob
import json
import requests

training = ""

for path in glob.iglob('labelbox/*.json'):
    with open(path) as json_file:
        data = json.load(json_file)
        for i in range(len(data)):
            try:
                filename = data[i]['External ID']
                orig_url = data[i]['Labeled Data']
                url = data[i]['Label']['objects'][0]['instanceURI']
                #print(url)
                res_label = requests.get(url)
                res_label.raise_for_status()
                open('labelbox/'+filename, 'wb').write(res_label.content)

                res_orig = requests.get(orig_url)
                res_orig.raise_for_status()
                open('input/'+filename, 'wb').write(res_orig.content)

                input_line = 'training/input/'+filename
                print(input_line)

                img = cv2.imread('labelbox/'+filename)
                hsv=img

                # Define lower and uppper limits of what we call "brown"
                white=np.array([255,255,255])

                # Mask image to only select white
                mask=cv2.inRange(hsv,white,white)
                #mask_inv = [not m for m in mask]

                # Change image colors
                img[mask==0]=(0,0,255)
                img[mask>0]=(255,0,255)

                path = path.split('/')[-1]
                cv2.imwrite('color_corrected/labeled_'+filename,img)
                output_line = 'training/color_corrected/labeled_'+filename
                print(output_line)

                training += input_line + ' ' + output_line + '\n'
            except:pass

with open("training.txt", "w+") as myfile:
    myfile.write(training)
