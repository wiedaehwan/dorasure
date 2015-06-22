# coding: utf-8

import numpy as np
import random
from collections import Counter, deque
from operator import itemgetter

COLS = 6
ROWS = 5
# Fire, Water, Tree, Light, Dark, Heal, oJama, Poison
DROPS_COMBINATION = {'ALL': 'FWTLDHJP',
                     'NORMAL': 'FWTLDH',
                     '3COLOR': 'FWTH',
                     'NO_LIGHT': 'FWTDH',
                     'NO_DARK': 'FWTLH',
                     'NO_HEAL': 'FWTLD'}
CURRENT_DROP_COMBINATION = 'NORMAL'
BLOCK_NUMBER = 100
BLOCK_NAME = 'X'


class Drop(int):
    def __init__(self, *args, **kwargs):
        super(Drop, self).__init__(self, *args, **kwargs)
        self.name = DROPS_COMBINATION[CURRENT_DROP_COMBINATION][self] if self < BLOCK_NUMBER else BLOCK_NAME
        self.fixed = 0


class Solver:
    def __init__(self, rows=ROWS, cols=COLS, drops='NORMAL'):
        global CURRENT_DROP_COMBINATION
        CURRENT_DROP_COMBINATION = drops
        self.rows = rows
        self.cols = cols
        self.board_size = rows * cols
        self.board_size_with_block = rows + 1 * cols + 1
        self.drops = DROPS_COMBINATION[drops]
        self.drop_size = len(self.drops)
        self.board = self.init_board()
        self.__diagonal = 2

    @property
    def diagonal(self):
        return self.__diagonal

    @diagonal.setter
    def diagonal(self, v):
        # 1 is 8-direction   2 is 4-direction
        self.__diagonal = v and 1 or 2

    def init_map_board(self):
        board = np.array(self.board)
        map_board = np.arange(self.rows * self.cols).reshape(self.rows, self.cols)
        print board[:self.rows, :self.cols]
        board[:self.rows, :self.cols] = map_board
        return board

    def init_board(self):
        board = [0 for _ in range((self.rows + 1) * (self.cols + 1))]
        for i, b in enumerate(board):
            if ((i + 1) % (self.cols + 1)) == 0 or i >= ((self.cols + 1) * self.rows):
                board[i] = Drop(100)
        return board

    def print_board(self, block=0, name=0):
        block = int(bool(block))
        if name:
            board = map(lambda x: getattr(x, 'name'), self.board)
        else:
            board = self.board
        print np.array(board).reshape(self.rows + 1, self.cols + 1)[:self.rows + block, :self.cols + block]

    def randomize_board(self):
        for j in range(self.rows):
            for i in range(self.cols):
                self.board[i + j + j * self.cols] = Drop(random.choice(range(self.drop_size)))
        self.get_most_drop()

    def get_most_drop(self, name=0):
        if name:
            board = map(lambda x: getattr(x, 'name'), self.board)
        else:
            board = self.board
        board = np.array(board).reshape(self.rows + 1, self.cols + 1)[:self.rows, :self.cols]
        self.most_drop = Counter(board.flatten()).most_common(self.drop_size)

    def get_start_drop(self):
        for i in range(1, 4):
            for item, count in self.most_drop:
                if count % 3 == i:
                    return item
        return item

    def print_most_drop(self, name=0):
        print self.get_most_drop(name=name)

    def find_next(self):
        pass

    def find_matches(self):
        pass

    def update_most_drop(self):
        new_most_drop = []
        new_temp_drop = []
        for name, count in self.most_drop:
            for i in range(count // 3):
                new_most_drop.append(name, 3)
            if count % 3:
                for i in range(count % 3):
                    new_temp_drop.insert(0, name)

if __name__ == '__main__':
    solver = Solver()
    solver.randomize_board()
    solver.print_board(block=1, name=1)
    solver.print_board()
    solver.print_most_drop(name=1)
    solver.print_most_drop()
    print solver.get_start_drop()
    print solver.init_map_board()