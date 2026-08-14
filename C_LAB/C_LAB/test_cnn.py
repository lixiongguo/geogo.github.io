import torch
import torchvision
import torchvision.transforms as transforms
from torch import nn
import torch.nn.functional as F
from PIL import Image
import os
import matplotlib.pyplot as plt
from torchsummary import summary
import numpy as np
import time
import cv2

# train_loader = torch.utils.data.DataLoader(train_data,batch_size=64,
#                                           shuffle=True,num_workers=2)
# test_loader = torch.utils.data.DataLoader(test_data,batch_size=64,
#                                           shuffle=True,num_workers=2)

class CNN_Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 32, kernel_size=8, stride=4, padding=2)
        self.relu1 = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)
        self.relu2 = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool2d(2, 2)
       
        self.fc1 = nn.Linear(64 * 5 * 7, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 2)
    def forward(self, x):
        
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.softmax(self.fc3(x),dim=1)
        return x
    
random_tensor = torch.rand(1,4,60, 40)
cnn_net = CNN_Net()
print(cnn_net(random_tensor))
# summary(cnn_net,(4,40,60))