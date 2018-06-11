#!/usr/bin/env python
"""
train value_network using the TD(lambda) reinforcement algorithm
"""
from engine import *
from node import *
from value_network import *
from noughts_crosses import *


def create_train_sequence(engines):
    'create a forest of nodes, their roots a new board position'
    board = initialBoard
    trace = []
    player = players[0]
    index = 0
    while evaluate(board) is None:
        node = engines[index].create_search_tree(board, player)
        trace.append(node)
        board = node.pv.board 
        player = next_player(player)
        index = int(not index)
    node = Node(board)
    node.reward = evaluate(board)
    trace.append(node)
    return trace


def TD_Lambda(engines, network):
    'return sequence of boards and reward for training'
    trace = create_train_sequence(engines)
    boards = [t.board for t in trace]
    reward = trace[-1].reward
    network.temporal_difference(boards, reward)
        

if __name__ == "__main__":
    valueNetwork = ValueNet(0.01, 0.7)
    e = Engine(valueNetwork, 9)
    TD_Lambda([e, e], valueNetwork)
