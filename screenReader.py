# coding: utf-8

import numpy
from PIL import Image

# THIS SETTINGS FOR SAMSUNG GALAXY NOTE II
ROWS = 5
COLS = 6
WIDTH = 720
HEIGHT = 1280
SCREEN_SHOT = 'screen.png'
COLOR = {'fire': (179, 98, 84),
         'water': (106, 132, 165),
         'wood': (94, 152, 111),
         'light': (169, 154, 97),
         'dark': (145, 91, 140),
         'heart': (173, 86, 124)}


def __round(array):
    return int(round(numpy.average(array)))


def get_rgb(pic, box=None):
    if box is None:
        pic_width, pic_height = pic.size
        box = (0, 0, pic_width, pic_height)
    rgb_img = pic.crop(box)
    rgb = numpy.array(rgb_img.getdata())
    return [__round(rgb[:, 0]),
            __round(rgb[:, 1]),
            __round(rgb[:, 2])]


def get_orb(array):
    _max = 0
    result = None
    for k, c in COLOR.iteritems():
        tmp = numpy.corrcoef(numpy.array(array), numpy.array(c))[0][1]
        if _max < tmp:
            result = k
            _max = tmp
    assert (result is not None)
    return result


def get_board():
    pil_img = Image.open(SCREEN_SHOT, 'r')
    # cropping board
    width, height = pil_img.size
    pil_img = pil_img.crop((4, 690, width - 8, height))
    # initializing
    width, height = pil_img.size
    orb_size = width / COLS
    xa = 0
    xb = xa + orb_size
    xs = orb_size
    ya = height - ROWS * orb_size
    yb = ya + orb_size
    ys = orb_size
    # creating board
    new_board = []
    for i in xrange(ROWS):
        new_board.append([])
        for j in xrange(COLS):
            new_board[i].append([])
            box = (xa + xs * j,
                   ya + ys * i,
                   xb + xs * j,
                   yb + ys * i)
            rgb = get_rgb(pil_img, box)
            orb = get_orb(rgb)
            new_board[i][j] = orb

    return new_board

# test code
if __name__ == '__main__':
    print get_board()
