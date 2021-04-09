import numpy as np
import torch
from torch import nn
from torch import optim
import torch.nn.functional as F

import matplotlib.pyplot as plt
from torchvision import datasets, transforms, models

from torch.utils.data.sampler import SubsetRandomSampler

data_dir = 'images/train/'


def load_split_train_test(datadir, valid_size = .2):

    train_transforms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),])
    test_transforms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),])

    train_data = datasets.ImageFolder(datadir, transform=train_transforms)
    test_data = datasets.ImageFolder(datadir, transform=test_transforms)

    num_train = len(train_data)
    indices = list(range(num_train))
    split = int(np.floor(valid_size * num_train))
    np.random.shuffle(indices)
    train_idx, test_idx = indices[split:], indices[:split]

    train_sampler = SubsetRandomSampler(train_idx)
    test_sampler = SubsetRandomSampler(test_idx)

    trainloader = torch.utils.data.DataLoader(train_data, sampler = train_sampler, batch_size=64)
    testloader = torch.utils.data.DataLoader(test_data, sampler=test_sampler, batch_size=64)
    return trainloader, testloader

trainloader, testloader = load_split_train_test(data_dir, .2)
print(trainloader.dataset.classes)

# start CNN ALGORITHM ResNet50
model = models.resnet50(pretrained=True)
print(model)

for param in model.parameters():
    param.requires_grad = False

# Rectified Linear Unit activation function, (sigmoid function)
model.fc = nn.Sequential(nn.Linear(2048,512),
                         nn.ReLU(),
                         nn.Dropout(0.2),
                         nn.Linear(512,10),
                         nn.LogSoftmax(dim=1))

criterion = nn.NLLLoss()
device = torch.device("cpu")

optimizer = optim.Adam(model.fc.parameters(), lr=0.003)
epochs = 1
steps = 0
running_loss = 0
print_every = 10
train_losses, test_losses = [], []

# Training weights for custom images
for epoch in range(epochs):
    for inputs, labels in trainloader:
        steps += 1
        input, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        logps = model.forward(input)
        loss = criterion(logps, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if steps % print_every == 0:
            test_loss = 0
            accuracy = 0
            model.eval()
            with torch.no_grad():
                for inputs, labels in testloader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    logps = model.forward(inputs)
                    batch_loss = criterion(logps, labels)
                    test_loss += batch_loss.item()
            #TRAINING FUNCTION
            model.train()
torch.save(model, "cat_model.pth")




