import logging
import sys
import os
import json
import pickle
import random

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable

from nn.utils import level, xp, ranked, lossStreak, winStreak, wins, played, Net

logger = logging

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
    m = []
    
    for participant in participants:
        if participant is not None:
            print str(type(participant))
            m += [ wins(participant.wins),
                   ranked(participant.played_ranked),
                   winStreak(participant.winStreak),
                   played(participant.played),
                   lossStreak(participant.lossStreak),
                   level(participant.level),
                   xp(participant.xp),
                   float(random.randint(0, 30)) # Random hero selected
                 ]      
        else:
            m += [ 0,
               0,
               0,
               0,
               0,
               0,
               0,
               float(random.randint(0, 30)) # Random hero selected
             ]
    
    X.append(m)

    if os.path.exists("nn/nn.dat"):
        with open("nn/nn.dat", "r") as nn_dat:
            net = pickle.load(nn_dat)
    else:
        print "No neural network present"
        return -1
        
    net.eval()

    # Verification
    output = net.forward(Variable(torch.FloatTensor([X[0]])))

    return output.data[0].select(0, 0)
