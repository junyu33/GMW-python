#!/usr/bin/python3           
# gates.py
def AND(a, b):
    return a & b

def OR(a, b):
    return a | b

def NOT(a):
    return int(not a)

def G(bit1, bit2):
    not_bit1 = NOT(bit1)
    result = AND(not_bit1, bit2)
    return NOT(result)


