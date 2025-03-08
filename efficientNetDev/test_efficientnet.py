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

# image_dir   = "./object_classification_batch_1/"
# label_path  = "./object_classification_batch_1.csv"
odd_ths     = 2
class_path  = "./classes.txt"
# make label's hot encoding
# label   = pd.read_csv(label_path,header=None,names=['filename','class']).reset_index(drop=True).set_index('class')
# # load the classes, make classes hot encoded
classes = pd.read_csv(class_path,header=None,names=['class'])
classes = classes.join(pd.get_dummies(classes)).set_index('class')
# label   = label.join(classes,how='inner').reset_index(drop=True).set_index('filename')




transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to the size required by EfficientNet-B2
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# dataset = MenuDataset(image_dir,label,transform)
# menuloader = DataLoader(dataset,batch_size=batch_size,shuffle=False)


# load model
# Define EfficientNet-B2
model = models.efficientnet_b2(pretrained=False)
num_classes = len(classes)
model.classifier[1] = nn.Linear(model.classifier[1].in_features,num_classes)

model.load_state_dict(torch.load(f"./trained_model/train2.pth"))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
model.eval()

parser = argparse.ArgumentParser(description="Load an image with a formatted filename.")
parser.add_argument("image_path", type=str, help="Image Path, include extension")
parser.add_argument("imsz", type=int, help="Image size.")

im = Image.open(parser.parse_args().image_path)
npim = np.array(im)

# Define patch size and step
imsz = (parser.parse_args().imsz)
step = imsz // 2  # 256-pixel overlap
patch_id = 0

menus = set()
odds = list()
for i in range(0, npim.shape[0] - imsz + 1, step):
    for j in range(0, npim.shape[1] - imsz + 1, step):
        print(i,j)
        # Crop the image patch
        patch = npim[i:i + imsz, j:j + imsz]

        # Convert NumPy array back to PIL image
        patch_im = Image.fromarray(patch)
        patch_im = patch_im.transpose(Image.ROTATE_270)
        patch_im = patch_im.convert('RGB')
        prediction = model(transform(patch_im).unsqueeze(0)).detach()
        whichmenu = torch.argmax(prediction[0])
        odd = torch.max(prediction[0])

        menuname = classes.columns.to_list()[whichmenu].replace('class_','')
        if odd > odd_ths:
            menus.add(menuname)
            odds.append(odd)


print(menus)