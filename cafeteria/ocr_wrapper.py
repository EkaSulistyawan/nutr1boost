import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
import os
from tqdm import tqdm
import pandas as pd
from PIL import Image
import numpy as np
import argparse
import easyocr

class ocr:
    def __init__(self,prob_ths=0.5,imsz=700,device='cpu'):
        self.device = device
        self.reader = easyocr.Reader(['ja'])
        
        self.prob_ths = prob_ths
        self.imsz = imsz


    def predict(self,im):
        npim = np.array(im)
        npim = np.rot90(npim, k=-1)  
        step = self.imsz // 2  # 256-pixel overlap

        response = {}

        for i in range(0, npim.shape[0] - self.imsz + 1, step):
            for j in range(0, npim.shape[1] - self.imsz + 1, step):
                print(i,j)
                # Crop the image patch
                patch = npim[i:i + self.imsz, j:j + self.imsz]
                result = self.reader.readtext(patch)

                # crop_im = Image.fromarray(patch)
                # crop_filename = f"./ocr_output/crop_{i}_{j}.png"
                # crop_im.save(crop_filename)  # Save the cropped image

                if result:
                    highest_result = max(result, key=lambda item: item[2])
                    if (highest_result[2] > self.prob_ths):
                        response[highest_result[1]] = highest_result[2]

        return response