## KPar: Using Python as a configuration system (even for non Python code)

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
root.car.name = 'supercar'
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
# file: boards/board_1.py
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
# file: boards/board_2.py
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
    root.car.electronics.computers[k].board = load('boards/board_%i.py' % k).board
```

Notice that the `load` method is almost like a regular Python import which returns the global environment of the loaded file. It differs from a regular Python import because the name of the file to be imported can be a string and therefore it can be constructed programmatically. The path to the file is always relative to the folder of the loading file.

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
python3 -m pip install kpar
kpar-process --output_prefix "example/report" example/car.py:root
```

or programmatrically:

```
from kpar import process
process('example/car.py', 'root', 'example/report')
```

This will generate:

[report.json](example/output/report.json): a JSON serialized version of the root object which can be fed to another program in any language that can read JSON.

[report_types.csv](example/output/report_types.csv): a CSV list of parameters and their types. Diffing two of this files allows to determine if parameters have been added or deleted or if their type has changed.

[report_hashes.csv](example/output/report_hashes.csv): a CSV list of parameters and hashes of their value. Diffing two of these files allows to check which values have changed.

[report_provenance.csv](example/output/report_provenance.csv): A CSV list of parameters and where (filename, line number) they are defined.

### Caveat 1

While the root can have and arbitrary name and one can have multiple ``Obj``ects, there must be only one root since all paths are relative to the one root.

### Caveat 2

You can assign any object to a KPar `Obj()` but it will be injested and recursively transformed. Only bool, long, float, and strings can be leafs unless a value is wrapped into `naive(...)`.

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
    print(key, '=', repr(value))
```

produces:

```
car.test1.a = 2
car.test1.b.c = 3
car.test2.x = 5
car.test2.y = 6
car.test3 = {'a': 2, 'b': {'c': 3}}
```

## Unit conversions

KPar supports dimensional unit conversions

```
from kpar import u

x = 2*u.milliyards
y = 3*u.weeks
z = 4*u.kilograms
s = (x + x)*z / y**2
t = float(s)
```

In this example x,y,z,s ar dimensional objcts, t is a double. 
Arthmetic operations are only allowed between numerical objects with comparable dimensions.
The python `float` operator converts the value into a numeric value in the international system. 

Once a dimensional object is assigned to a kpar Obj it is automatically converted to a 
double precision value in the Internation System and the dimensionality info is lost in the generated JSON.
For example:

```
from kpar import u, Obj

root = Obj()
root.car.speed = 120*u.miles/u.hour
```

Notice kpar understands units both sngular and plural and allows prefixes like nano, mega, kilo, etc.

You can also do explicit conversions using the % operator. 

```
root.piston.accel = (10*u.nanolightyears/u.megaweeks**2) % (u.meters/u.second**2)
```

Explicit conversions allows to convert from any units to any compatible units and raises 
an exception when units are not compatible.

### Python versions

We support python3 only

### How do I try it?

```
git clone git@github.com:mdipierro/kpar.git
cd kpar
make install
cd example
kpar-process car.py:root
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

The units system is ported from https://github.com/mdipierro/buckingham
