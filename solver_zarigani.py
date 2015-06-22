# coding: utf-8
import numpy as np
import random
from collections import Counter, deque
from copy import deepcopy

PUZZLE_COLUMNS = 6
PUZZLE_ROWS = 5


class Drop:
    def __init__(self, name='X'):
        self.name = name
        self.fixed = False

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __nonzero__(self):
        return self.fixed


class Board:
    drops = 'FWTLDHJP'
    __route_dic = ['R', 'DR', 'D', 'DL', 'L', 'UL', 'U', 'UR']

    def __init__(self, cols=PUZZLE_COLUMNS, rows=PUZZLE_ROWS):
        self.cols = cols
        self.rows = rows
        self.size = self.rows * self.cols
        self.__board = self.init_board()
        self.cursor = 0
        self.__diagonal = 2

    @property
    def diagonal(self):
        return self.__diagonal

    @diagonal.setter
    def diagonal(self, v):
        # 1 is 8-direction   2 is 4-direction
        self.__diagonal = v and 1 or 2

    @property
    def board(self):
        return tuple(drop.name for drop in self.__board)

    @board.setter
    def board(self, b):
        self.__board = b

    def init_board(self):
        board = [Drop() for _ in range(self.size)]
        return board

    def print_out(self, board=None):
        if board is None:
            board = self.board
        else:
            board = tuple(board)
        for j in xrange(self.rows):
            s = slice(self.cols * j, self.cols * j + self.cols)
            print board[s]

    def randomize_board(self):
        for i in range(self.size):
            self.__board[i] = Drop(random.choice(self.drops))

    def get_most_drop(self):
        return Counter(self.board).most_common(len(self.drops))

    def set_cursor(self):
        for name, count in self.get_most_drop():
            if count % 3 == 1:
                break
        self.cursor = self.board.index(name)

    def can_move_cursor(self, d, cursor):
        col, row = self.pos_as_2d(cursor)
        if d == 0:
            return col < self.cols - 1
        elif d == 1:
            return row < self.rows - 1 and col < self.cols - 1
        elif d == 2:
            return row < self.rows - 1
        elif d == 3:
            return row < self.rows - 1 and col > 0
        elif d == 4:
            return col > 0
        elif d == 5:
            return row > 0 and col > 0
        elif d == 6:
            return row > 0
        elif d == 7:
            return row > 0 and col < self.cols - 1
        return False

    def move_cursor(self, d, cursor):
        col, row = self.pos_as_2d(cursor)
        if d == 0:
            col += 1
        elif d == 1:
            row += 1; col += 1
        elif d == 2:
            row += 1
        elif d == 3:
            row += 1; col -= 1
        elif d == 4:
            col -= 1
        elif d == 5:
            row -= 1; col -= 1
        elif d == 6:
            row -= 1
        elif d == 7:
            row -= 1; col += 1
        return self.pos_as_1d(col, row)

    def pos_as_1d(self, i, j):
        assert (0 <= i < self.cols)
        assert (0 <= j < self.rows)
        return j * self.cols + i

    def pos_as_2d(self, i):
        return i % self.cols, i // self.cols

    def get_next(self, board, cursor):
        for d in range(0, 8, self.diagonal):
            if self.can_move_cursor(d, cursor):
                target_index = self.move_cursor(d, cursor)
                result = list(board)
                result[cursor], result[target_index] = board[target_index], board[cursor]
                yield d, tuple(result), target_index

    def solve(self):
        queue = deque([(deepcopy(self.board), [], deepcopy(self.cursor))])
        seen = set()
        # while queue:
        board, route, cursor = queue.popleft()
        seen.add((board, cursor))
        if board == (1, 2, 3, 4, 5, 6, 7, 8, 0):
            return route
        for direction, new_board, new_cursor in self.get_next(board, cursor):
            if (new_board, new_cursor) not in seen:
                route.append(direction)
                queue.append((new_board, route, new_cursor))
        return route

    def translate_route(self, route):
        print tuple(self.__route_dic[i] for i in route)

    def get_drop(self, i):
        return self.__board[i]

    def create_pieces(self, most_drop):
        queue = deque([])
        for drop, num in most_drop:
            for i in range(num // min(3, self.cols, self.rows)):
                p = Piece(drop, [list(range(min(3, max(self.cols, self.rows))))])
                queue.appendleft(p)
            if num % min(3, self.cols, self.rows):
                p = Piece(drop, [list(range(num % min(3, max(self.cols, self.rows))))])
                queue.append(p)
        return list(queue)


class Piece:
    formsize = 0
    name = ''

    def __init__(self, name, form):
        self.name = name
        self.used = 0
        self.form = form
        self.formsize = len(self.form)

    def __repr__(self):
        return '%r-%r' % (self.name, self.form)


class PieceSolver:
    def __init__(self, queue, cols=PUZZLE_COLUMNS, rows=PUZZLE_ROWS):
        self.board = None
        self.cols = cols
        self.rows = rows
        self.init_level = 0
        self.counter = 0
        self.try_counter = 0
        self.pp = queue
        self.init_board()

    def init_board(self):
        # boardの初期化
        self.board = [0 for _ in range((self.rows + 1) * (self.cols + 1))]
        for i, b in enumerate(self.board):
            if ((i + 1) % (self.cols + 1)) == 0 or i >= ((self.cols + 1) * self.rows):
                self.board[i] = 100

    def print_board(self):
        print 'No. %d' % self.counter
        print np.array(self.board).reshape(self.rows + 1, self.cols + 1)[:self.rows, :self.cols]

    def board_index(self, find_num, start_pos):
        for i in range(start_pos, (self.cols + 1) * (self.rows + 1)):
            if self.board[i] == find_num:
                return i
        return 0

    # パズルの解を求める
    def try_piece(self, x, lvl):
        print 'try_piece called'
        self.try_counter += 1
        x = self.board_index(0, x)
        for i in range(len(self.pp)):
            print 'try %d...' % i
            if self.pp[i].used:
                continue
            for j in range(len(self.pp[i].form)):
                sum = 0
                print np.array(self.board).reshape(self.rows + 1, self.cols + 1)
                for k in range(len(self.pp[i].form[j])):
                    sum += self.board[x + self.pp[i].form[j][k]]
                if sum:
                    continue
                # ピースを置く
                for k in range(len(self.pp[i].form[j])):
                    self.board[x + self.pp[i].form[j][k]] = i + 1
                self.pp[i].used = 1
                # すべてのピースを置ききったらTrueを返す（recursiveコールの終了）
                if lvl == len(self.pp) - 1:
                    self.counter += 1
                    self.print_board()
                    # ピースを戻す
                    for k in range(len(self.pp[i].form[j])):
                        self.board[x + self.pp[i].form[j][k]] = 0
                    self.pp[i].used = 0
                    return True
                # 次のピースを試す
                self.try_piece(x + 1, lvl + 1)
                # ピースを戻す
                for k in range(len(self.pp[i].form[j])):
                    self.board[x + self.pp[i].form[j][k]] = 0
                self.pp[i].used = 0


if __name__ == '__main__':
    b = Board(6, 5)
    b.randomize_board()
    b.print_out()
    most = b.get_most_drop()
    # b.translate_route(b.solve())
    print 'most_drop is', most
    print 'using "%s" at %d' % (b.get_drop(b.cursor).name, b.cursor)
    p = PieceSolver(b.create_pieces(most), 6, 5)
    print 'p.pp', p.pp

    print p.try_piece(0, 0)
    print 'counter', p.counter
    print 'try counter', p.try_counter
