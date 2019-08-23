from kpar import *
from car import root

for key, value, typ, provenance in to_list(root):
    print(key, repr(value), 'of type', repr(typ.__name__))
    for filename, lineno in provenance[:1]:
        print('  was defined in file', filename, 'at line', lineno)
    for filename, lineno in provenance[1:]:
        print('  was re-defined in file', filename, 'at line', lineno)
