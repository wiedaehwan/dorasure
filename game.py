# coding: utf-8
# coding: utf-8

import pygame, random, time, sys
from pygame.locals import *
import itertools
import os

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

MARGIN = 2
SHAPE_WIDTH = 100 + 2 * MARGIN
SHAPE_HEIGHT = 100 + 2 * MARGIN
PUZZLE_COLUMNS = 6
PUZZLE_ROWS = 5
WINDOW_WIDTH = PUZZLE_COLUMNS * SHAPE_WIDTH
WINDOW_HEIGHT = PUZZLE_ROWS * SHAPE_HEIGHT

MINIMUM_MATCH = 3
FPS = 30
EXPLOSION_SPEED = 15
REFILL_SPEED = 10


class Cell(object):
    def __init__(self, image):
        self.offset = 0.0
        self.image = image
        self.alpha = 255

    def tick(self, dt):
        self.offset = max(0.0, self.offset - dt * REFILL_SPEED)


class Board(object):
    def __init__(self, width, height):
        self.explosion = range(255, 0, -70)
        shapes = 'fire water tree light dark heart'
        self.shapes = [pygame.image.load('images/{}_block.png'.format(shape))
                       for shape in shapes.split()]
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill((0, 0, 0))
        self.blank = pygame.image.load('images/blank_block.png')
        self.w = width
        self.h = height
        self.size = width * height
        self.board = [Cell(self.blank) for _ in xrange(self.size)]
        self.matches = []
        self.refill = []
        self.explosion_time = 0

    def randomize(self):
        for i in range(self.size):
            self.board[i] = Cell(random.choice(self.shapes))

    def pos(self, i, j):
        assert (0 <= i < self.w)
        assert (0 <= j < self.h)
        return j * self.w + i

    def busy(self):
        return self.refill or self.matches

    def tick(self, dt):
        if self.refill:
            for c in self.refill:
                c.tick(dt)
                c.alpha = 255
            self.refill = [c for c in self.refill if c.offset > 0]
            if self.refill:
                return
        elif self.matches:
            self.explosion_time += dt
            f = int(self.explosion_time * EXPLOSION_SPEED)
            if f < len(self.explosion):
                self.update_matches(None, alpha=self.explosion[f])
                return
            self.update_matches(self.blank)
            self.refill = list(self.refill_columns())
            self.find_matches()
        self.explosion_time = 0

    def draw(self, display):
        display.blit(self.background, (0, 0))
        for i, c in enumerate(self.board):
            self.blit_alpha(display, c.image,
                            (MARGIN + SHAPE_WIDTH * (i % self.w),
                             MARGIN + SHAPE_HEIGHT * (i // self.w - c.offset)),
                            c.alpha)

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        # temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)

    def swap(self, dropId, currentDropId):
        """
        Swap the two board cells covered by `dropId` and update the
        matches.
        """
        i = self.pos(*dropId)
        ci = self.pos(*currentDropId)
        b = self.board
        b[i], b[ci] = b[ci], b[i]

    def find_matches(self):
        """
        Search for matches (lines of cells with identical images) and
        return a list of them, each match being represented as a list
        of board positions.
        """

        def lines():
            for j in range(self.h):
                yield range(j * self.w, (j + 1) * self.w)
            for i in range(self.w):
                yield range(i, self.size, self.w)

        def key(i):
            return self.board[i].image

        def matches():
            for line in lines():
                for _, group in itertools.groupby(line, key):
                    match = list(group)
                    if len(match) >= MINIMUM_MATCH:
                        yield match

        matches = list(matches())
        self.matches = matches
        print matches

    def update_matches(self, image, alpha=0):
        """
        Replace all the cells in any of the matches with `image`.
        """
        for match in self.matches:
            for position in match:
                if image != None:
                    self.board[position].image = image
                else:
                    self.board[position].alpha = alpha

    def refill_columns(self):
        """
        Move cells downwards in columns to fill blank cells, and
        create new cells as necessary so that each column is full. Set
        appropriate offsets for the cells to animate into place.
        """
        for i in range(self.w):
            target = self.size - i - 1
            for pos in range(target, -1, -self.w):
                if self.board[pos].image != self.blank:
                    c = self.board[target]
                    c.image = self.board[pos].image
                    c.offset = (target - pos) // self.w
                    target -= self.w
                    yield c
            offset = 1 + (target - pos) // self.w
            for pos in range(target, -1, -self.w):
                c = self.board[pos]
                c.image = random.choice(self.shapes)
                c.offset = offset
                yield c


class Game(object):
    """
    The state of the game, with properties:
    `clock` -- the pygame clock.
    `display` -- the window to draw into.
    `font` -- a font for drawing the score.
    `board` -- the board of cells.
    `cursor` -- the current position of the (left half of) the cursor.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PAD Clone")
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),
                                               DOUBLEBUF)
        self.board = Board(PUZZLE_COLUMNS, PUZZLE_ROWS)

    def start(self):
        """
        Start a new game with a random board.
        """
        self.board.randomize()
        self.dropId = None
        self.dragging = False

    def quit(self):
        """
        Quit the game and exit the program.
        """
        pygame.quit()
        sys.exit()

    def play(self):
        """
        Play a game: repeatedly tick, draw and respond to input until
        the QUIT event is received.
        """
        self.start()
        self.find_matches()
        while True:
            self.draw()
            dt = min(self.clock.tick(FPS) / 1000.0, 1.0 / FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                elif event.type == KEYUP:
                    self.input(event.key)
                elif event.type == MOUSEBUTTONDOWN:
                    self.drag(MOUSEBUTTONDOWN)
                elif event.type == MOUSEBUTTONUP:
                    self.drag(MOUSEBUTTONUP)
                elif event.type == MOUSEMOTION:
                    self.drag(MOUSEMOTION)

            self.board.tick(dt)

    def getLeftTopOfTile(self, x, y):
        left = (x * SHAPE_WIDTH) + (x - 1)
        top = (y * SHAPE_HEIGHT) + (y - 1)
        return (left, top)

    def getDropId(self, pos):
        x, y = pos
        for i in xrange(PUZZLE_COLUMNS):
            for j in xrange(PUZZLE_ROWS):
                left, top = self.getLeftTopOfTile(i, j)
                tileRect = pygame.Rect(left, top, SHAPE_WIDTH, SHAPE_HEIGHT)
                if tileRect.collidepoint(x, y):
                    return (i, j)
        return None

    def drag(self, state):
        if self.board.busy():
            self.dragging = False
            return
        if state == MOUSEBUTTONDOWN:
            self.dropId = self.getDropId(pygame.mouse.get_pos())
            self.dragging = True
        elif state == MOUSEMOTION and self.dragging:
            currentDropId = self.getDropId(pygame.mouse.get_pos())
            if currentDropId != None and self.dropId != currentDropId:
                self.swap(currentDropId)
                self.dropId = currentDropId
        elif state == MOUSEBUTTONUP:
            self.find_matches()
            self.dragging = False

    def input(self, key):
        """
        Respond to the player pressing `key`.
        """
        if key == K_q:
            self.quit()

    def swap(self, currentDropId):
        self.board.swap(self.dropId, currentDropId)

    def find_matches(self):
        self.board.find_matches()

    def draw(self):
        self.board.draw(self.display)
        pygame.display.update()


if __name__ == '__main__':
    Game().play()
