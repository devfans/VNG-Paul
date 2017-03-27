import sys
import os
import json
import pickle
import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

from utils import level, xp, ranked, lossStreak, winStreak, wins, played

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.main = nn.Sequential(
            nn.Linear(len(X[0]),96),
            nn.Sigmoid(),
            nn.Dropout(p=0.1),
            nn.Linear(96,64),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(64,32),
            nn.Sigmoid(),
            nn.Dropout(p=0.1),
            nn.Linear(32,16),
            nn.ReLU(),
            #nn.Dropout(p=0.1),
            nn.Linear(16,8),
            nn.Sigmoid(),
            #nn.Dropout(p=0.1),
            nn.Linear(8,1)
        )

    def forward(self, input):
        return self.main.forward(input)

def eval(participants):

    if len(participants) == 2:
        participants.insert(1, None)
        participants.insert(2, None)
        participants.insert(4, None)
        participants.insert(5, None)

    elif len(participants) == 4:        
        participants.insert(2, None)
        participants.insert(5, None)

    X = []
    
    for participant in participants:
        if participant is not None:
            print str(type(participant))
            X += [ wins(participant.wins),
                   ranked(participant.played_ranked),
                   winStreak(participant.winStreak),
                   played(participant.played),
                   lossStreak(participant.lossStreak),
                   level(participant.level),
                   xp(participant.xp),
                   float(random.randint(0, 30)) # Random hero selected
                 ]      
        else:
            X += [ 0,
               0,
               0,
               0,
               0,
               0,
               0,
               float(random.randint(0, 30)) # Random hero selected
             ]

    if os.path.exists("nn/nn.dat"):
        with open("nn/nn.dat", "r") as nn_dat:
            net = pickle.load(nn_dat)
    else:
        print "No neural network present"
        return -1
        
    net.eval()

    # Verification
    output = net.forward(Variable(torch.FloatTensor([X])))

    return output.data[0]
