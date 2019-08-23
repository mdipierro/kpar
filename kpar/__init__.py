import csv
import collections
import copy
import inspect
import json
import os
import re
import sys
import yaml

__version__ = '0.4'

assert sys.version[0] == '3'

__all__ = ['Obj', 'override', 'naive', 'clone', 'to_list', 'autoparse']

re_int = re.compile('^\d+$')
re_key = re.compile('^[\w_]+$')

class override(object):
    def __init__(self, true_value):
        self.true_value = true_value

class naive(object):
    def __init__(self, true_value):
        self.true_value = true_value

def clone(obj):
    if isinstance(obj, Obj):
        return Obj({keyfy(k): clone(obj[k]) for k in obj})
    return copy.deepcopy(obj)

def objectify(value):
    if isinstance(value, Obj):
        return value
    if hasattr(value, '__dict__'):
        value = value.__dict__
    if isinstance(value, dict):
        value = Obj(value)
    elif isinstance(value, (list, tuple)):
        value = Obj({keyfy(k): objectify(v) for k, v in enumerate(value)})
    return value

def keyfy(key):
    if re_int.match(key):
        return int(key)
    elif re_key.match(key):
        return key
    raise KeyError("key not supported")

class Obj(dict):
    definitions = collections.defaultdict(list)
    def update_definitions(self, key):
        for frame in inspect.stack():
            filename = frame[1]
            if filename != __file__:
                filename = os.path.abspath(filename)
                self.definitions[id(self), key].append((filename, frame[2]))
                return
    def __init__(self, *args, **kwargs):
        items = dict(*args, **kwargs)
        for key, value in items.items():
            key = keyfy(key)
            self[key] = objectify(value)
    def __getitem__(self, key):
        key = keyfy(key)
        if not key in self:
            self[key] = Obj()
        return dict.__getitem__(self, key)
    def __setitem__(self, key, value):
        key = keyfy(key)
        dict.__setitem__(self, key, value)
        self.update_definitions(key)
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, value):
        is_naive = isinstance(value, naive)
        is_override = isinstance(value, override)
        if key in self and not is_override:
            raise ValueError("Key already defined")
        elif key not in self and is_override:
            raise valueError("No default to override")
        if is_override or is_naive:
            value = value.true_value
        if not is_naive:
            value = objectify(value)
        self[key] = value

def to_list(obj, path=''):
    s = []
    for key in obj:
        value = obj[key]
        if isinstance(value, Obj):
            s += to_list(value, path=path+key+'.')
        else:
            s.append((path+key, value, type(value), obj.definitions[id(obj), key]))
    return s

def autoparse(value):
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return str(value)

def load(filename):
    if filename.endswith('.yaml'):
        return Obj(yaml.load(open(filename).read(), Loader=yaml.SafeLoader))
    if filename.endswith('.json'):
        return Obj(json.loads(open(filename).read()))
    if filename.endswith('.py'):       
        return __import__(filename[:-3].replace(os.path.sep, '.'))
    if filename.endswith('.csv'):
        return naive([list(map(autoparse, row)) for row in csv.reader(open(filename)) if row])
    return Obj()
