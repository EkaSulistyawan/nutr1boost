import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import pandas as pd
from PIL import Image
import numpy as np
import argparse

# custom data loader
class MenuDataset(Dataset):
    def __init__(self,image_dir,label,transform=None):
        self.image_dir      = image_dir
        self.image_list     = list(os.listdir(self.image_dir)) 
        self.label          = label
        self.transform      = transform
    def __len__(self):
        return len(self.image_list)
    def __getitem__(self,idx):
        image = Image.open(os.path.join(self.image_dir,self.image_list[idx])).convert('RGB')
        label = self.label.loc[self.image_list[idx],:].to_numpy().astype(float)

        if self.transform:
            image = self.transform(image)

        return image,label

batch_size = 8
num_epochs = 100

image_dir   = "./object_classification_batch_1/"
label_path  = "./object_classification_batch_1.csv"
class_path  = "./classes.txt"
trainidx    = 7

# make label's hot encoding
label   = pd.read_csv(label_path,header=None,names=['filename','class']).reset_index(drop=True).set_index('class')
# # load the classes, make classes hot encoded
classes = pd.read_csv(class_path,header=None,names=['class'])
classes = classes.join(pd.get_dummies(classes)).set_index('class')
label   = label.join(classes,how='inner').reset_index(drop=True).set_index('filename')

print(classes.columns)
