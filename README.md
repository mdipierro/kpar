## Using Python (with KPar) as a configuration system (even for non Python code)


Any complex software application needs to be configured using human readable and editable parameters. Examples of configurations systems are ConfigParser, Windows `.ini` files, and [Jasonnet](https://jsonnet.org/).

For an application example think of a complex mechanical system like a car where the parameters describe which parts comprise the car and how they should be assembled and what the properties of those parts are.

The car example perfectly illustrates some of the features that we expect from such configuration system:

**It should be hierarchical**. Think of the car as a root of a tree, with the engine and doors as nodes, and with pistons and screws as leafs of the tree.

**It should be extensible**. It should not depend on the specific system we are describing and we should be able adapt it to changes in specifications.

**It should be programmable**. This is counter-intuitive but some times it easier and less error prone to express configuration parameters using loops and conditionals. Think of an engine with 8 pistons. It is easier to loop and configure the pistons as function of their position than using constants. This makes it easier to change the configuration when the number of pistons changes.

**It should be organizable**. It should be possible to organize many configuration parameters into files. It should not dictate a file structure but should leave the users the option to do so.

**It should prevent syntactic mistakes**. It should prevent, for example, accidentally defining the same parameter in multiple places where one value silently overrides a previously defined value. It should prevent overriding a value that was never defined to begin with. It should prevent storing data structures that are not supported.

**It should allow static analysis**. It should be possible to verify without interpreting the values, that parameters are generated correctly and that parameters have the expected names and types. It should be possible to easily diff different versions of the output.

**It should allow specialization**. Once we have described a car, we may want to describe another car by overriding the parameters of the first car. And so on in order to describe multiple cars.

**It should track provenance**. We should be able to ask the system why a certain parameter has the value it has (aka. where was it set).

**It should be simple and concise**. We want to minimize the typing required to write the configurations.

**It should produce simple to parse output**. We want the output of our configuration system to be easy to parse in any language (not just Python) so that it can be ingested, for example, by a Java program.

If it seems we are describing a programming language it is because we are. Many configuration systems use text or yaml files generated using a template language. The Google Cloud Manager is an example that comes to mind. It works. It is ugly. It does not scale beyond a certain level of complexity.

Here we propose to use Python for writing configuration parameters but with the addition of a specialized class that enforces some of the above requirements, `Obj`.

`Obj` has the name suggests is the name of an `Obj`ect class. At its fundamental level it can be thought of as a `defaultdict` of `defaultdict`s with immutable values. This is better expressed with an example:

```
# file car.py
from kpar import *

root = Obj()
root.car.name = 'Toyota'
root.car.body.engine.num_pistons=4 
for k in range(root.car.body.engine.num_cilinders):
    root.car.body.engine.piston[k].position.x = 0
    root.car.body.engine.piston[k].position.y = 0
    root.car.body.engine.piston[k].position.z = 10*k
    root.car.body.engine.piston[k].diameter = 8*k
```

The code above is pure python code. We can verify it with pylint. We can run and import ``root`` from it.
There is more we can do. For example let's imagine the car has many electrical boards and each of them has its own complex set of parameters which we want to describe in its own files. For example:

```
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
```

```
# file: board_2.py
from kpar import *

# this board has a computer with a different name and fuse
board = clone(load('board_1.py').board)
board.name = override('secondary car computer')
board.fuse.blue.max_power = override(40)
```

Notice how the second board extends the former by cloning it and overriding parameters.
Re-assigning a key without overriding, results in an exception.
Overriding a key that was not previously defined, also results in an exception.

Now we can read this from our main `car.py` file:

```
# file: car.py
...
for k in (1, 2):
    root.car.electronics.computers[k].board = load('board_%i.py' % k).board
```

Notice that the `load` method is almost like a regular Python import which returns the global environment of the loaded file. It differs from a regular Python import because the name of the file to be imported can be a string and therefore it can be constructed programmatically. 

As with normal import you can import functions and call them and they can generate configuration parameters.

The `load` method does not replace the `import` function and you can use the latter as you
normally would.

Also notice that `load` is not limited to Python files. It can also load YAML, JSON, and CSV files.
You can create your own loaders.

```
# file: car.py
...
root.car.specs.info = load(root.car.name + '/info.yaml')
root.car.specs.hp_per_rpm = load(root.car.name + '/hp_rpm.csv')
```

The root object (the name is abritrary  - yes we could have called the root "car")
can then be used to access the desired information:

```
# file: report.py
from kpar import *
from car import root

for key, value, typ, provenance in to_list(root):
    print(key, repr(value), 'of type', repr(typ.__name__))
    for filename, lineno in provenance:
        print('  was defined in file', filename.split('/')[-1], 'at line', lineno)
```

Running `report.py` produces output like the following:

```
car.name 'Toyota' of type 'str'
  was defined in file car.py at line 5
car.body.engine.num_pistons 4 of type 'int'
  was defined in file car.py at line 6
car.body.engine.piston.0.position.x 0 of type 'int'
  was defined in file car.py at line 9
...
car.electronics.computers.1.board.name 'main car computer' of type 'str'
  was defined in file board_1.py at line 6
car.electronics.computers.1.board.fuse.red.max_power 10 of type 'int'
  was defined in file board_1.py at line 7
...
car.electronics.computers.2.board.fuse.blue.max_power 40 of type 'int'
  was defined in file board_2.py at line 5
  was defined in file board_2.py at line 7
...
```

The output of `to_list` is serializable in JSON, YAML, and CSV and can be used to check that
multiple runs of the code result in the same set of parameters and with the same types. You can 
check which files have indeed been loaded/imported and which lines have been used.

```
...
import json
print(json.dumps({key:value for key, value, _, _ in to_list(root)}))
```

The serialized parameters can be passed to a consuming application, for example a Java program.

Caveat: You can assign any object to a KPar `Obj()` but it will be inejcted and recursively transformed.
Only bool, long, float, and strings can be leafs unless a value is wrapped into `navie(...)`.

For example:

```
from kpar import *
root = Obj()

# injesting a dict
root.car.test1 = {'a': 2, 'b': {'c': 3}}

# injesting an arbitrary object
class A(): pass
a = A()
a.x = 5
a.y = 6
root.car.test2 = a

# naive injesting (no transformation)
root.car.test3 = naive({'a': 2, 'b': {'c': 3}})

# let's see the output
for key, value, typ, provenance in to_list(root)):
    print(key, '=', str(value))
```

produces:

```
car.test1.a = 2
car.test1.b.c = 3
car.test2.x = 5
car.test2.y = 6
car.test3 = {'a': 2, 'b': {'c': 3}}
```

### Python versions

We support python3 only

### How do I try it?

```
git clone git@github.com:mdipierro/kpar.git
cd kpar
make install
cd examples
python3 report.py > report.txt
```

and of course

```
python3 -m pip install kpar
```

### License

BSD

### Historical origin

This is a re-branding (with some cleanup) of a module that has been used
for web2py plugin configurations since 2009.
