# -*- coding: utf-8 -*-
"""hw5_skeleton.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15FYhAaWwf-7fq8yBujQBzPhkjWJfFAPz
"""

import torch
import torchvision

# import torch.utils.tensorboard as tb

from PIL import Image

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

import matplotlib.pyplot as plt
import pandas as pd

import csv

import os.path
import numpy as np

LABEL_NAMES = {'background':0, 'kart':1, 'pickup':2, 'nitro':3, 'bomb':4, 'projectile':5}

LABEL_=['background','kart','pickup','nitro','bomb','projectile']

"""## Reading Data"""

# upload the data and unzip it. You will see data/ with train/ and valid/. 
# !unzip supertux_classification_trainval.zip

"""## Defining Torch Dataset"""

class SuperTuxDataset(Dataset):
    def __init__(self, image_path,data_transforms=None):
        """
        Hint: Use the python csv library to parse labels.csv
        """
        if data_transforms is None:
            self.supertux_transform = transforms.Compose([transforms.ToTensor()])
        else:
            self.supertux_transform = data_transforms

        self.data_transforms = data_transforms
        self.image_path = image_path
        # read the csv labels file
        self.supertux_csv = pd.read_csv(self.image_path+'/labels.csv', header=0)
        # slice the label column 
        self.supertux_label = self.supertux_csv.loc[:,'label'].tolist()
        # slice the name of images 
        self.name = self.supertux_csv.loc[:,'file'].tolist()

        # load the images
        self.image_loc = self.image_path+'/'+self.supertux_csv.loc[:,'file']
        self.image_loc =  self.image_loc.tolist()
        self.supertux_image = []

        # for img_loc in self.image_loc:
        #   self.supertux_image.append(transforms.ToTensor()(Image.open(img_loc)))

    def __len__(self):
        return len(self.supertux_label)

    def __getitem__(self, idx):
        """
        return a tuple: img, label
        """
        # item_image = self.supertux_image[idx]
        item_name = self.name[idx]
        item_image = self.supertux_transform(Image.open(self.image_path+'/'+item_name))
        item_label = LABEL_NAMES[self.supertux_label[idx]]    # must give back the integer not the string
        return (item_image, item_label)

"""The following utility visualizes the data, optionally, as a sanity check for your implementation of the dataset class. Call visualize_data() after setting the correct variables inside this code snippet."""

def visualize_data():

    Path_to_your_data= '/content/data/train'
    dataset = SuperTuxDataset(image_path=Path_to_your_data)

    f, axes = plt.subplots(3, len(LABEL_NAMES))

    counts = [0]*len(LABEL_NAMES)

    for img, label in dataset:
        c = counts[label]

        if c < 3:
            ax = axes[c][label]
            ax.imshow(img.permute(1, 2, 0).numpy())
            ax.axis('off')
            ax.set_title(LABEL_[label])
            counts[label] += 1
        
        if sum(counts) >= 3 * len(LABEL_NAMES):
            break

    plt.show()

# visualize_data()

"""## Defining Model Architecture and Loss"""

import  torch.nn.functional as tf
class ClassificationLoss(torch.nn.Module):

    def forward(self, input, target):
        """
        Your code here
        Compute mean(-log(softmax(input)_label))
        @input:  torch.Tensor((B,C)), where B = batch size, C = number of classes
        @target: torch.Tensor((B,), dtype=torch.int64)
        @return:  torch.Tensor((,))
        Hint: Don't be too fancy, this is a one-liner
        """
        loss = -tf.log_softmax(input, dim = 1)     # log softmax loss 
        return torch.mean(torch.gather(loss, 1, target.view(-1,1)))

import torch.nn as nn
class CNNClassifier(torch.nn.Module):
    
    def __init__(self):
        """
        Your code here
        """

        num_classes = 6

        super(CNNClassifier, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=3, out_channels=12, kernel_size=5,stride=1, padding=2)
        self.relu1 = nn.ReLU()
        self.maxpool1 = nn.MaxPool2d(kernel_size=2) # resized down to 32*32
        
        self.conv2 = nn.Conv2d(in_channels=12, out_channels=24, kernel_size=5, stride=1, padding=2)
        self.relu2 = nn.ReLU()
        
        self.fc1 = nn.Linear(in_features=32 * 32 * 24, out_features=num_classes)

    def forward(self, x):
        """
        Your code here
        @x: torch.Tensor((B,3,64,64))
        @return: torch.Tensor((B,6))
        """

        x = self.conv1(x)
        x = self.relu1(x)
        
        x = self.maxpool1(x)
        
        x = self.conv2(x)
        x = self.relu2(x)
        
        x = x.view(-1, 32 * 32 * 24)
        x = self.fc1(x)
        return x

from torch import save
from torch import load
from os import path

def save_model(model):
    if isinstance(model, CNNClassifier):
        print('Model saved!!!')
        # return save(model.state_dict(), path.join(path.abspath(''), 'cnn.th'))
        return save(model.state_dict(), path.join('/content/model', 'cnn.th'))
    
    raise ValueError("model type '%s' not supported!"%str(type(model)))


def load_model():
    r = CNNClassifier()
    # r.load_state_dict(load(path.join(path.abspath(''), 'cnn.th'), map_location='cpu'))
    r.load_state_dict(load(path.join('/content/model', 'cnn.th'), map_location='cpu'))
    return r

"""## Tensorboard logging"""

def test_logging(train_logger, valid_logger):

    """
    Your code here.
    Finish logging the dummy loss and accuracy
    Log the loss every iteration, the accuracy only after each epoch
    Make sure to set global_step correctly, for epoch=0, iteration=0: global_step=0
    Call the loss 'loss', and accuracy 'accuracy' (no slash or other namespace)
    """

    """
    Your code here.
    Finish logging the dummy loss and accuracy
    Log the loss every iteration, the accuracy only after each epoch
    Make sure to set global_step correctly, for epoch=0, iteration=0: global_step=0
    Call the loss 'loss', and accuracy 'accuracy' (no slash or other namespace)
    """
    # train_logger and valid_logger are the tb.SummaryWriter

    # This is a strongly simplified training loop
    train_loss_list = []
    train_acc_list = []
    valid_acc_list = []
    criterion = ClassificationLoss()

    for epoch in range(10):
        torch.manual_seed(epoch)
        for iteration in range(20):
            dummy_train_loss = 0.9 ** (epoch + iteration / 20.)
            dummy_train_accuracy = epoch / 10. + torch.randn(10)

            train_loss_list.append(dummy_train_loss)  # store the loss in list
            train_acc_list.append(dummy_train_accuracy.mean().item())
            train_logger.add_scalar('train/loss', dummy_train_loss, epoch * 20 + iteration)

            # dummy_train_accuracy = criterion()
            # logger.add_scalar('train/loss', dummy_train_loss, iteration)
            # raise NotImplementedError('Log the training loss')
        train_logger.add_scalar('train/accuracy', np.asarray(train_acc_list).mean(), epoch)

        torch.manual_seed(epoch)
        for iteration in range(10):
            dummy_validation_accuracy = epoch / 10. + torch.randn(10)
            valid_acc_list.append(dummy_validation_accuracy.mean().item())
        valid_logger.add_scalar('valid/accuracy', np.asarray(valid_acc_list).mean(), epoch)
    train_logger.close()
    valid_logger.close()

"""After implementing `test_logging()`, call it below. This should produce some plots on your tensorboard."""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

# Commented out IPython magic to ensure Python compatibility.
# %reload_ext tensorboard

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# from torch.utils.tensorboard import SummaryWriter
# ROOT_LOG_DIR = './logdir'

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir {ROOT_LOG_DIR} #Launch tensorboard

# train_logger = tb.SummaryWriter(path.join('./logdir', 'train'))      # os. is added
# valid_logger = tb.SummaryWriter(path.join('./logdir', 'test'))
# test_logging(train_logger, valid_logger)

"""**Training and evaluation utility functions** 

Here are some implementations of useful functions for training and evaluating your models. Read these carefully. You may need to make some obvious edits before these will work.
"""

def accuracy(outputs, labels):
    outputs_idx = outputs.max(1)[1].type_as(labels)
    return outputs_idx.eq(labels).float().mean()

def predict(model, inputs, device='cpu'):
    inputs = inputs.to(device)
    logits = model(inputs)
    return F.softmax(logits, -1)
    
def draw_bar(axis, preds, labels=None):
    y_pos = np.arange(6)
    axis.barh(y_pos, preds, align='center', alpha=0.5)
    axis.set_xticks(np.linspace(0, 1, 10))
    
    if labels:
        axis.set_yticks(y_pos)
        axis.set_yticklabels(labels)
    else:
        axis.get_yaxis().set_visible(False)
    
    axis.get_xaxis().set_visible(False)

def visualize_predictions():
  
    model = load_model()
    model.eval()

    validation_image_path='/content/data/valid' #enter the path 

    dataset = SuperTuxDataset(image_path=validation_image_path)

    f, axes = plt.subplots(2, 6)

    idxes = np.random.randint(0, len(dataset), size=6)

    for i, idx in enumerate(idxes):
        img, label = dataset[idx]
        preds = predict(model, img[None], device='cpu').detach().cpu().numpy()

        axes[0, i].imshow(TF.to_pil_image(img))
        axes[0, i].axis('off')
        draw_bar(axes[1, i], preds[0], LABEL_ if i == 0 else None)

    plt.show()

"""## Training models

The `load_data` utility below uses your implementation of the dataset class above to provide a helper function that might be useful when you train your models. You won't need to change anything inside this function.
"""

def load_data(dataset_path, data_transforms=None, num_workers=0, batch_size=128):
    dataset = SuperTuxDataset(dataset_path,data_transforms)
    return DataLoader(dataset, num_workers=num_workers, batch_size=batch_size, shuffle=True)

"""But you *will* need to implement `train()`, which takes an `args` object, that could have arbitrary arguments inside. We won't test your train function directly, but will instead evaluate the model it produces as output. To call `train`, you have to first create an args object, and add various attributes to it, as shown below:"""

class Args(object):
    def __init__(self):
        self.learning_rate = 0.01
        self.batch_size_train = 128
        self.batch_size_valid = 128

        # parameters for optimizer
        self.epochs = 10
        self.momentum = 0.9
        self.weight_decay = 0

        # data directory
        self.dir_train = '/content/data/train'
        self.dir_valid = '/content/data/valid'

        # log parameters
        self.log_dir = './my_tensorboard_log_directory'
        self.log_thres = 50

# Add attributes to args here, such as:
# args.learning_rate = 0.0001
# args.log_dir = './my_tensorboard_log_directory'

"""Then implement `train`. Follow the instructions in the assignment."""

def train(args):
    """
    Your code here
    """
    loss_train = []
    acc_train = []
    acc_valid = []
    total_loss = 0
    log_iter = 0
    # ======== This part is written referred to the Pytorch tutorial =========

    if args.log_dir is not None:
        train_logger = tb.SummaryWriter(path.join(args.log_dir, 'train'))
        valid_logger = tb.SummaryWriter(path.join(args.log_dir, 'valid'))
    # raise NotImplementedError('train')

    model = CNNClassifier()
    # model = load_model().to(device)  #########
    args.learning_rate = 0.01
    args.epochs = 5

    criterion = ClassificationLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=args.learning_rate, momentum=args.momentum,
                                weight_decay=args.weight_decay)

    data_train = load_data(args.dir_train, batch_size=args.batch_size_train)
    data_valid = load_data(args.dir_valid, batch_size=args.batch_size_valid)

    for epc in range(args.epochs):  # epc starts from 0
        model.train()
        # shuffle the dataset at every epoch
        for batch_i, (data_i, target_i) in enumerate(data_train):  # may be changed into (input, target)
            # get the inputs
            temp_input, temp_target = data_i, target_i  # .to(device)

            # zero the parameter gradient
            optimizer.zero_grad()

            # forward backward optimize
            temp_output = model(temp_input)
            loss = criterion(temp_output, temp_target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            # print statistics
            if batch_i % args.log_thres == 0:
                loss_train.append(loss.item())  # store loss
                train_logger.add_scalar('train/loss', loss.item(), log_iter)
                print('[%d, %5d] loss: %.3f' %
                      (epc + 1, batch_i + 1, total_loss / args.log_thres))
                total_loss = 0.0
                log_iter += 1

        # fit and get accuracy
        model.eval()
        for batch_i, data_i in enumerate(data_valid):  # load the valid data
            input_valid, label_valid = data_i
            temp_acc_valid = accuracy(model(input_valid), label_valid).item()
            acc_valid.append(temp_acc_valid)
        mean_acc_valid = np.asarray(acc_valid).mean()  # get the mean accuracy
        print('Valildation Accuracy:' + str(mean_acc_valid))
    save_model(model)

# train(args)
# torch.cuda.empty_cache()

"""Now, you can call `train` with `train(args)`, where `args` contains your various favorite settings of hyperparameters and other arguments that your implementation of `train` needs.


Afterwards, you can call `predict()' and `visualize_predictions()' to evaluate your model.
"""