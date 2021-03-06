#!/usr/bin/env python
"""
Value Network based on Giraffe
"""
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import torch
torch.manual_seed(1729)
np.random.seed(1729)
import copy


class ValueNet(nn.Module):
    """
    Value Network Layers, Architecture and forward pass
    """
    def __init__(self, learningRate, decay):
        'initialise all the layers and activation functions needed'
        super(ValueNet, self).__init__()

        self.learningRate = learningRate
        self.weightsNum = 0
        self.decay = decay
        
        # three layers
        self.fc1 = nn.Linear(9, 128)
        self.fc2 = nn.Linear(128, 32)
        self.fc3= nn.Linear(32, 1)

        # if cuda, use GPU
        self.gpu = False #torch.cuda.is_available()
        if self.gpu:
            self.cuda()

            
    def list_to_Variable(self, inputLayer, grad):
        'convert a list to Variable for use in PyTorch'
        inputLayer = [0 if iL == None else iL for iL in inputLayer]
        inputLayer = torch.FloatTensor(np.array(inputLayer))
        if self.gpu:
            inputLayer = inputLayer.cuda()
        return Variable(inputLayer, requires_grad=grad)
    

    def forward_pass(self, out):
        'forward pass using Variable inputLayer'
        out = self.fc1(out)
        out = F.relu(out)
        out = self.fc2(out)
        out = F.relu(out)
        out = self.fc3(out)
        #out = F.dropout(out, training=self.training)
        return F.tanh(out)
    
    
    def forward(self, inputLayer):
        'forward pass using Variable inputLayer'
        inputLayer = self.list_to_Variable(inputLayer, False)
        return self.forward_pass(inputLayer).data[0]
    

    def load_weights(self):
        'load name'
        self.load_state_dict(torch.load("weights.h5"))
    
    
    def save_weights(self, directory):
        'save the weights as the number in "directory/"'
        self.weightsNum += 1
        name = directory + "/" +  str(self.weightsNum) + ".h5"
        print name
        torch.save(self.state_dict(), name)

    
    def temporal_difference(self, boards, lastValue, discount):
        'backup values according to boards'
        traces, gradients, trace = [], [], 0.0
        # boards goes forward in time, so reverse index
        for i in range(len(boards)-1, -1, -1):
            board = self.list_to_Variable(boards[i], True)
            value = self.forward_pass(board)
            # compute eligibility trace
            difference = discount * lastValue - value.data[0]
            trace = trace * discount * self.decay + difference
            traces.append(trace)
            # zero gradients and compute partial differential wrt parameters
            for p in self.parameters():
                if p.grad is not None:
                    p.grad.data.zero_()
            lastValue = value.data[0]
            value.backward()
            grad = []
            for p in self.parameters():
                grad.append(copy.deepcopy(p.grad.data))
            gradients.append(grad)
            #print "gen", gradients[-1][0][0]
        # update the parameters of the network
        for (t, grad) in zip(traces, gradients):
            for (p, g) in zip(self.parameters(), grad):
                p.data += self.learningRate * t * g
            #print grad[0][0]


# from noughts_crosses import *
# v = ValueNet(0.5, 0.7)
# v.temporal_difference([initialBoard], 1.0)
