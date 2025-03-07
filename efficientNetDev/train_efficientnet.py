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
trainidx    = 6

# make label's hot encoding
label   = pd.read_csv(label_path,header=None,names=['filename','class']).reset_index(drop=True).set_index('class')
# # load the classes, make classes hot encoded
classes = pd.read_csv(class_path,header=None,names=['class'])
classes = classes.join(pd.get_dummies(classes)).set_index('class')
label   = label.join(classes,how='inner').reset_index(drop=True).set_index('filename')

transform = transforms.Compose([
    transforms.RandomResizedCrop(224,scale=(0.8,1.0)),
    transforms.ToTensor(),
    transforms.ColorJitter(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

dataset = MenuDataset(image_dir,label,transform)
menuloader = DataLoader(dataset,batch_size=batch_size,shuffle=False)


# load model
# Define EfficientNet-B2
model = models.efficientnet_b2(pretrained=False)
num_classes = len(classes)
model.classifier[1] = nn.Linear(model.classifier[1].in_features,num_classes)

model.load_state_dict(torch.load(f"./trained_model/train{trainidx}_100.pth"))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)

# training
for epoch in range(num_epochs):
    model.train()
    avg_loss = 0 
    imtrain,labeltrain = next(iter(menuloader))
    tq =tqdm(menuloader)
    for imtrain, labeltrain in tq:
        optimizer.zero_grad()

        imtrain, labeltrain = imtrain.to(device),labeltrain.to(device)
        outp = model(imtrain)

        loss = criterion(outp,labeltrain)
        loss.backward()
        optimizer.step()

        tq.set_postfix(loss=loss.item())


torch.save(model.state_dict(), f"./trained_model/train{trainidx+1}_100.pth")