#!/usr/bin/env python3
"""
student.py

UNSW COMP9444 Neural Networks and Deep Learning

You may modify this file however you wish, including creating additional
variables, functions, classes, etc., so long as your code runs with the
hw2main.py file unmodified, and you are only using the approved packages.

You have been given some default values for the variables train_val_split,
batch_size as well as the transform function.
You are encouraged to modify these to improve the performance of your model.

"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

"""
   Answer to Question:

Briefly describe how your program works, and explain any design and training
decisions you made along the way.
"""

############################################################################
######     Specify transform(s) to be applied to the input images     ######
############################################################################
def transform(mode):
    """
    Called when loading the data. Visit this URL for more information:
    https://pytorch.org/vision/stable/transforms.html
    You may specify different transforms for training and testing
    """
    if mode == 'train':
        tf = transforms.Compose([
            transforms.RandomAffine(degrees=0, translate=(0.2,0.2)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
        ])

        # return transforms.ToTensor()
        return tf
    elif mode == 'test':
        return transforms.ToTensor()


############################################################################
######   Define the Module to process the images and produce labels   ######
############################################################################
class Network(nn.Module):

    def __init__(self):
        super().__init__()

        
    def forward(self, input):
        pass

class LinNet(nn.Module):

    def __init__(self, num_hid):
        super().__init__()
        # self.fc1 = nn.Linear(3*80*80,num_hid)
        # self.fc2 = nn.Linear(num_hid + (3*80*80), num_hid)
        # self.fc3 = nn.Linear(num_hid + num_hid + (3*80*80), 8)
        # self.fc4 = nn.Linear()
        self.linear_layer = nn.Sequential(
            nn.Linear(3*80*80,num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, num_hid),
            nn.ReLU(),
            nn.Linear(num_hid, 8)           
        )


        
    def forward(self, input):
        # # print(f"input shape: {input.shape}")
        # input = input.view(200,-1)
        # # print(f"adjusted input shape: {input.shape}")
        # self.hid1 = torch.tanh(self.fc1(input))
        # self.hid2 = torch.tanh(self.fc2(torch.cat((input,self.hid1),dim=1)))
        # self.output = self.fc3(torch.cat((input,self.hid1,self.hid2),dim=1))
        # # print(f"Output Shape: {self.output.shape}")

        input = input.view(200, -1)
        self.output = self.linear_layer(input)
        return self.output

class ConvNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.convolutional_layer = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=6, kernel_size=(5,5)),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(2,2),stride=(2,2),padding=0),
            nn.Conv2d(in_channels=6, out_channels=16, kernel_size=(5,5)),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(2,2),stride=(2,2),padding=0),
            nn.Conv2d(in_channels=16, out_channels=120, kernel_size=(5,5)),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(2,2),stride=(2,2),padding=0),
            nn.Conv2d(in_channels=120, out_channels=120, kernel_size=(5,5)),
            nn.ReLU()          
        )

        self.linear_layer = nn.Sequential(
            nn.Dropout(),
            nn.Linear(in_features=2*2*120, out_features=84),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(in_features=84, out_features=84),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(in_features=84, out_features=8),
            nn.ReLU()
        )
        
    def forward(self, input):
        input = self.convolutional_layer(input)
        # print(f"input shape: {input.shape}")
        input = input.view(-1,2*2*120)
        output = self.linear_layer(input)  
        return output


class Block(nn.Module):
    def __init__(self, in_channels, out_channels, identity_downsample=None, stride=1):
        super(Block, self).__init__()
        self.num_layers = 18
        self.expansion = 1

        # self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        # self.bn1 = nn.BatchNorm2d(out_channels)        
        self.conv2 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(out_channels, out_channels * self.expansion, kernel_size=1, stride=1, padding=0)
        self.bn3 = nn.BatchNorm2d(out_channels * self.expansion)
        self.relu = nn.ReLU()
        self.identity_downsample = identity_downsample

    def forward(self, input):
        identity = input
        input = self.conv2(input)
        input = self.bn2(input)
        input = self.relu(input)
        input = self.conv3(input)
        input = self.bn3(input)

        if self.identity_downsample is not None:
            identity = self.identity_downsample(identity)

        input += identity
        input = self.relu(input)
        return input



class ResNet(nn.Module):
    def __init__(self, block, image_channels, num_classes):
        super(ResNet, self).__init__()
        self.num_layers = 18
        self.expansion = 1

        self.in_channels = 64
        self.conv1 = nn.Conv2d(image_channels, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)


        self.layer1 = self.make_layers(self.num_layers, block, 2, intermediate_channels=64, stride=1)
        self.layer2 = self.make_layers(self.num_layers, block, 2, intermediate_channels=128, stride=2)
        self.layer3 = self.make_layers(self.num_layers, block, 2, intermediate_channels=256, stride=2)
        self.layer4 = self.make_layers(self.num_layers, block, 2, intermediate_channels=512, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * self.expansion, num_classes)    


    def forward(self, input):
        input = self.conv1(input)
        input = self.bn1(input)
        input = self.relu(input)
        input = self.maxpool(input)

        input = self.layer1(input)
        input = self.layer2(input)
        input = self.layer3(input)
        input = self.layer4(input)

        input = self.avgpool(input)
        input = input.reshape(input.shape[0], -1)
        input = self.fc(input)
        return input       

    def make_layers(self, num_layers, block, num_residual_blocks, intermediate_channels, stride):
        layers = []

        identity_downsample = nn.Sequential(nn.Conv2d(self.in_channels, intermediate_channels*self.expansion, kernel_size=1, stride=stride),
                                            nn.BatchNorm2d(intermediate_channels*self.expansion))
        layers.append(block(self.in_channels, intermediate_channels, identity_downsample, stride))
        self.in_channels = intermediate_channels * self.expansion # 256
        for i in range(num_residual_blocks - 1):
            layers.append(block(self.in_channels, intermediate_channels)) # 256 -> 64, 64*4 (256) again
        return nn.Sequential(*layers)


# net = Network()
# net = LinNet(60)
# net = ConvNet()
net = ResNet(Block, 3, 8)
    
############################################################################
######      Specify the optimizer and loss function                   ######
############################################################################
optimizer = optim.Adam(net.parameters(),lr=0.001, betas=(0.9,0.999), weight_decay=0.0001)

loss_func = nn.CrossEntropyLoss()


############################################################################
######  Custom weight initialization and lr scheduling are optional   ######
############################################################################

# Normally, the default weight initialization and fixed learing rate
# should work fine. But, we have made it possible for you to define
# your own custom weight initialization and lr scheduler, if you wish.
def weights_init(m):
    return

scheduler = None

############################################################################
#######              Metaparameters and training options              ######
############################################################################
dataset = "./data"
train_val_split = 0.8
batch_size = 200
epochs = 200
