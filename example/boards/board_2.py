# file: board_2.py
from kpar import *

# this board has a computer with a different name and fuse
board = clone(load('board_1.py').board)
board.name = override('secondary car computer')
board.fuse.blue.max_power = override(40)
