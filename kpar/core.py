import argparse
import csv
import collections
import copy
import hashlib
import importlib.util
import inspect
import json
import os
import re
import sys
import yaml
from urllib.request import urlopen


re_int = re.compile('^\d+$')
re_key = re.compile('^[\w_]+$')


class override(object):
    def __init__(self, true_value):
        self.true_value = true_value


class naive(object):
    def __init__(self, true_value):
        self.true_value = true_value


def objectify(value):
    """converts almost anything to an Obj()"""
    if isinstance(value, Obj):
        return value
    if hasattr(value, '__float__'):
        return float(value)
    if hasattr(value, '__dict__'):
        value = value.__dict__
    if isinstance(value, dict):
        value = Obj(value)
    elif isinstance(value, (list, tuple)):
        value = Obj({keyfy(k): objectify(v) for k, v in enumerate(value)})
    return value


def keyfy(key):
    """validates alphanumeric keys and returns an int if the key consists of digits"""
    key = str(key)
    if re_int.match(key):
        return int(key)
    elif re_key.match(key):
        return key
    raise KeyError("key %s not supported" % repr(key))


def get_top_frame():
    """find the first frame not in this file""" 
    for frame in inspect.stack():
        if frame[1] != __file__:
            return frame


class Obj(dict):
    """a defaultdict of defacultdicts of immutable values"""

    _definitions = collections.defaultdict(list)
    _root_path = None

    def update_definitions(self, key):
        """stores the file and line being executed, associated to (self, key)"""
        frame = get_top_frame()
        filename = os.path.abspath(frame[1])
        if not Obj._root_path:
            Obj._root_path = os.path.dirname(filename)
        common = os.path.commonprefix([Obj._root_path, filename])
        relative_path = os.path.relpath(filename, common)
        Obj._definitions[id(self), key].append((relative_path, frame[2]))

    def __init__(self, *args, **kwargs):
        """works as a dict constructor"""
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
        is_override = isinstance(value, override)
        if key in self and not is_override:
            raise ValueError("Key already defined")
        elif key not in self and is_override:
            raise valueError("No default to override")
        if is_override:
            value = value.true_value
        if isinstance(value, naive):
            value = value.true_value
        else:
            value = objectify(value)
        self[key] = value


def clone(obj):
    """can clone an Obj()"""
    if isinstance(obj, Obj):
        return Obj({keyfy(k): clone(obj[k]) for k in obj})
    return copy.deepcopy(obj)


def to_list(obj, path=''):
    s = []
    for key in obj:
        value = obj[key]
        if isinstance(value, Obj):
            s += to_list(value, path=path+str(key)+'.')
        else:
            s.append((path+str(key), value, type(value), Obj._definitions[id(obj), key]))
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


def load(filename, stream=None):
    filename = os.path.join(os.path.dirname(get_top_frame()[1]), filename)
    lfilename = filename.lower()
    if stream == None and lfilename.endswith(('.yaml','.json','.csv')):
        stream = open(filename)
    if lfilename.endswith('.yaml'):
        return Obj(yaml.load(stream.read(), Loader=yaml.SafeLoader))
    if lfilename.endswith('.json'):
        return Obj(json.loads(stream.read()))
    if lfilename.endswith('.csv'):
        return naive([list(map(autoparse, row)) for row in csv.reader(stream) if row])
    if filename.endswith('.py'):       
        module_name = filename.replace(os.path.sep, '.').rstrip('.py')
        spec = importlib.util.spec_from_file_location("kpar.temp.%s" % module_name, filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return Obj()


def process(filename, object_name, prefix):
    obj = getattr(load(filename), object_name)
    # generate csv
    with open(prefix + '_types.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(('Name', 'Type'))
        for row in to_list(obj):
            writer.writerow((row[0], row[2].__name__))
    # generate values
    with open(prefix + '_hashes.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(('Name', 'HashValue'))
        for row in to_list(obj):
            writer.writerow((row[0], hashlib.md5(repr(row[1]).encode()).hexdigest()))
    # generate provenance
    with open(prefix + '_provenance.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(('Name', 'Filname', 'LineNumber'))
        for row in to_list(obj):
            for filename, line in row[3]:
                writer.writerow((row[0], filename, line))
    # generate json
    with open(prefix + '.json', 'w') as fp:
        json.dump(obj, fp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="filename:object_name to load and process")
    parser.add_argument("--output_prefix", help="filename without extensions", default="report")
    args = parser.parse_args()
    filename, object_name = args.source.rsplit(':', 1)
    filename = os.path.join(os.getcwd(), filename)
    prefix = args.output_prefix
    process(filename, object_name, prefix)


if __name__ == '__main__':
    main()
