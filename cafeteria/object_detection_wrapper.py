import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
import os
from tqdm import tqdm
import pandas as pd
from PIL import Image
import numpy as np
import argparse

class object_detection:
    def __init__(self,odd_ths=2,imsz=512,device='cpu'):
        self.device = device
        # load classes
        class_path  = "./cafeteria/static/assets/classes.txt"
        self.classes = pd.read_csv(class_path,header=None,names=['class'])
        self.classes = self.classes.join(pd.get_dummies(self.classes)).set_index('class')
        # load transformation
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),  # Resize to the size required by EfficientNet-B2
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        # load model
        self.model = models.efficientnet_b2(pretrained=False)
        num_classes = len(self.classes)
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features,num_classes)
        self.model.load_state_dict(torch.load(f"./cafeteria/static/assets/train2.pth"))
        self.model.to(self.device)
        self.model.eval()
        
        self.odd_ths = odd_ths
        self.imsz = imsz


    def predict(self,im):
        npim = np.array(im)
        step = self.imsz // 2  # 256-pixel overlap

        menus = list()
        odds = list()

        for i in range(0, npim.shape[0] - self.imsz + 1, step):
            for j in range(0, npim.shape[1] - self.imsz + 1, step):
                print(i,j)
                # Crop the image patch
                patch = npim[i:i + self.imsz, j:j + self.imsz]

                # Convert NumPy array back to PIL image
                patch_im = Image.fromarray(patch)
                patch_im = patch_im.transpose(Image.ROTATE_270)
                patch_im = patch_im.convert('RGB')
                prediction = self.model(self.transform(patch_im).unsqueeze(0)).detach()
                whichmenu = torch.argmax(prediction[0])
                odd = torch.max(prediction[0])

                menuname = self.classes.columns.to_list()[whichmenu].replace('class_','')
                if odd > self.odd_ths:
                    if menuname not in menus:
                        menus.append(menuname)
                        odds.append(odd.item())

        print(menus,odds)
        return {
            'menus':menus,
            'odd':odds
        }