from . core import *
from . units import u

assert sys.version[0] == '3'

__all__ = ['Obj', 'load', 'override', 'naive', 'clone', 'to_list', 'autoparse', 'objectify', 'u']
__version__ = '0.7'
