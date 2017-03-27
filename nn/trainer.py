import sys
import os
import json
import pickle

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

from nn.utils import heroNameToInt, level, xp, ranked, lossStreak, winStreak, wins, played, Net


print "Loading matches data..."

files = os.listdir('Matches/') # Previously collected and prepared matches data
matches = []

for file in files:
    with open('Matches/' + file, 'r') as f:
        matches.append(json.loads(f.read()))

print "Matches loaded"

print "Trimming the data..."
X = []
Y = []

total = 0
for match in matches:
    # Just keep standard and battle royale matches that were completed 
    if match['data']['attributes']['stats']['endGameReason'] != "victory" or match['data']['attributes']['stats']['queue'] not in ['ranked', 'casual', 'casual_aral']:
        continue
        
    matchData = []
    resultData = None
    for roster_id, roster in match['rosters'].iteritems():
        if resultData is None:
            resultData = [1.0 if roster['winner'] else 0.0]
            Y.append(resultData)
            total = total + 1
        for participant_id, participant in roster['participants'].iteritems():
            matchData += [ wins(participant['player']['attributes']['stats']['wins']),
                       ranked(participant['player']['attributes']['stats']['played_ranked']),
                       winStreak(participant['player']['attributes']['stats']['winStreak']),
                       played(participant['player']['attributes']['stats']['played']),
                       lossStreak(participant['player']['attributes']['stats']['lossStreak']),
                       level(participant['player']['attributes']['stats']['level']),
                       xp(participant['player']['attributes']['stats']['xp']),
                       float(heroNameToInt(participant['attributes']['actor']))
                     ]

    X.append(matchData)

print "Total matches kept: {}".format(total)

print "Neural network training..."
        
if os.path.exists("nn.dat"):
    print "Previous neural network found, trying to pick up work where left..."
    with open("nn.dat", "r") as nn_dat:
        net = pickle.load(nn_dat)
else:
    net = Net()
net.cuda()
net.train()

optimizer = optim.Adam(net.parameters(), lr=0.0001)
#optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
criterion = nn.MSELoss()

input = Variable(torch.FloatTensor(X).cuda())
target = Variable(torch.FloatTensor(Y).cuda())

print "Starting training..."

try:
    for i in xrange(100000000): # arbitrary limit

        optimizer.zero_grad()
        output = net.forward(input)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        l = loss.data[0] # current loss
        if l < 0.15:
            break

        if(i % 100 == 99):
            print "Iteration={} Loss={}".format(i, loss.data[0])
except KeyboardInterrupt:
    pass

print "Training stopped"

net.eval()
net.cpu()

# Verification
#output = net.forward(Variable(torch.FloatTensor([X[2]])))
#print(Y[2])
#print(output.data[0])

print "Saving neural network on disk..."

with open("nn.dat", "w") as nn_dat:
    pickle.dump(net, nn_dat)
    
print "Neural network saved"
