# file car.py
from kpar import *

root = Obj()
root.car.name = 'Toyota'
root.car.body.engine.num_pistons=4

for k in range(root.car.body.engine.num_pistons):
    root.car.body.engine.piston[k].position.x = 0
    root.car.body.engine.piston[k].position.y = 0
    root.car.body.engine.piston[k].position.z = 10*k
    root.car.body.engine.piston[k].diameter = 8*k

for k in (1,2):
    root.car.electronics.computers[k].board = load('board_%i.py' % k).board

root.car.specs.info = load(root.car.name + '/info.yaml')
root.car.specs.hp_per_rpm = load(root.car.name + '/hp_rpm.csv')

        
