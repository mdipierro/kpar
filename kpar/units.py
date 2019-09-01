#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created by Massimo Di Pierro (http://experts4solutions.com) @2016 BSDv3 License                         
Extracted from https://github.com/mdipierro/buckingham

Projects gets it name from
http://en.wikipedia.org/wiki/Buckingham_%CF%80_theorem Buckingham
"""

import re
import math

__all__ = ['u']
    
UNITS = {
    'meter':  (1.0,1,0,0,0,0,0), # meter
    'second': (1.0,0,1,0,0,0,0), # second
    'gram':   (1.0,0,0,1,0,0,0), # gram
    'ampere': (1.0,0,0,0,1,0,0), # ampere
    'kelvin': (1.0,0,0,0,0,1,0), # kelvin
    'dollar': (1.0,0,0,0,0,0,1), # dollar
    'currency': (1.0,0,0,0,0,0,1), # currency
    'coulomb': (1.0,0,1,0,1,0,0), # one ampere x 1 second
    'angstrom': (10**-10,1,0,0,0,0,0),
    'atm': (101325000.0,-1,-2,1,0,0,0),
    'au':  (149597870691.0,1,0,0,0,0,0),
    'bar': (100000000.0,-1,-2,1,0,0,0),
    'coulomb':(1.0,0,1,0,1,0,0),
    'day':(86400.0,0,1,0,0,0,0),
    'ev':(1.602176487e-16,2,-2,1,0,0,0),
    'eV':(1.602176487e-16,2,-2,1,0,0,0),
    'farad':(1000.0,-2,4,-1,2,0,0),
    'faraday':(9.64853399e4,0,1,0,1,0,0),    
    'foot':(381./1250,1,0,0,0,0,0),
    'hour':(3600.0,0,1,0,0,0,0),
    'henry':(1000.0,2,-2,1,-2,0,0),
    'hz':(1.0,0,-1,0,0,0,0),
    'inch':(127./5000.,1,0,0,0,0,0),
    'point':(127./360000,1,0,0,0,0,0),
    'joule':(1000.0,2,-2,1,0,0,0),
    'calorie':(4186.8,2,-2,1,0,0,0),
    'lightyear':(9460730472580800.0,1,0,0,0,0,0),
    'liter':(0.001,3,0,0,0,0,0),
    'mho':(0.001,-2,3,-1,2,0,0),
    'mile':(201168./125,1,0,0,0,0,0),
    'minute':(60.0,0,1,0,0,0,0),
    'week':(86400.0*7,0,1,0,0,0,0),
    'mmhg':(133322.387415,-1,-2,1,0,0,0),
    'newton':(1000.0,1,-2,1,0,0,0),
    'ohm':(1000.0,2,-3,1,-2,0,0),
    'pascal':(1000.0,-1,-2,1,0,0,0),
    'pound':(4448.2216152605,1,-2,1,0,0,0),
    'psi':(6894757.29316836,-1,-2,1,0,0,0),
    'quart':(473176473./125000000000,3,0,0,0,0,0),
    'siemens':(0.001,-2,3,-1,2,0,0),
    'volt':(1000.0,2,-3,1,-1,0,0),
    'watt':(1000.0,2,-3,1,0,0,0),
    'weber':(1000.0,2,-2,1,-2,0,0),
    'yard':(1143./1250,1,0,0,0,0,0),    
    'year':(3944615652./125,0,1,0,0,0,0),
    'fermi':(10.0**-15,1,0,0,0,0,0),
}

def extend_units(units):
    scales =  [
        ('yocto',10.0**-24),
        ('zepto',10.0**-21),
        ('atto',10.0**-18),
        ('femto',10.0**-15),
        ('pico',10.0**-12),
        ('nano',10.0**-9),
        ('micro',10.0**-6),
        ('milli',10.0**-3),
        ('centi',10.0**-2),
        ('deci',0.1),
        ('deka',10.0),
        ('hecto',10.0**2),
        ('kilo',10.0**3),
        ('mega',10.0**6),
        ('giga',10.0**9),
        ('tera',10.0**12),
        ('peta',10.0**15),
        ('exa',10.0**18),
        ('zetta',10.0**21),
        ('yotta',10.0**24),
        ]
    keys = [key for key in units]
    for name, conversion in scales:
        for key in keys:
            v = units[key]
            units[name+key] = (v[0]*conversion, v[1], v[2], v[3], v[4], v[5], v[6])
extend_units(UNITS)

class Number:

    def __init__(self, value, dims=(1.0,0,0,0,0,0,0,0)):
        self.value = value
        self.dims = dims

    def __call__(self, key):
        if not self.regex.match(key):
            raise SyntaxError('Invalid Dims')
        n = eval(dims.replace('^','**'),self.c_n) or 1
        l = buckingham(dims, self.c_l)
        t = buckingham(dims, self.c_t)
        m = buckingham(dims, self.c_m)
        a = buckingham(dims, self.c_a)
        k = buckingham(dims, self.c_k)
        d = buckingham(dims, self.c_d)
        self.value = n
        self.dims = (l,t,m,a,k,d)

    def __add__(self, other):
        assert self.dims == other.dims
        return Number(self.value + other.value, self.dims)

    def __sub__(self, other):
        assert self.dims == other.dims
        return Number(self.value + other.value, self.dims)

    def __mul__(self, other):
        if not isinstance(other, Number):
            return Number(self.value * other, self.dims)
        dims = tuple(self.dims[i] + other.dims[i] for i in range(6))
        return Number(self.value * other.value, dims)

    def __rmul__(self,other):
        return self*other

    def __truediv__(self, other):
        if not isinstance(other, Number):
            return Number(self.value/other, self.dims)
        dims = tuple(self.dims[i]-other.dims[i] for i in range(6))
        return Number(self.value/other.value, dims)

    def __rdiv__(self,other):
        if not isinstance(other, Number):
            other = Number(other)
        return other/self

    def __pow__(self,other):
        dims = tuple(self.dims[i]*other for i in range(6))
        return Number(self.value ** other, dims)

    def __mod__(self, other):
        assert self.dims == other.dims, "Incompatible dimensions"
        return (self/other).value

    def __float__(self):
        return self.value

class UnitsFactory:    
    def __getattr__(self, key):
        if key[-1] == 's' and key[:-1] in UNITS:
            key = key[:-1]
        if key not in UNITS:
            raise ValueError("Units %s not supported" % key)
        item = UNITS[key]
        return Number(item[0], tuple(item[1:7]))

u = UnitsFactory()

