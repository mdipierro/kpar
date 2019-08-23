# file: board_1.py
from kpar import *

# this board has a computer with a name and 3 fuses
board = Obj()
board.name = 'main car computer'
board.fuse.red.max_power = 10
board.fuse.green.max_power = 20
board.fuse.blue.max_power = 30
for color in board.fuse:
    board.fuse[color].brand = 'brand-a'
