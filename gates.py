#!/usr/bin/python3           
# gates.py
def AND(a, b):
    return a & b

def OR(a, b):
    return a | b

def NOT(a):
    return int(not a)

def XOR(a, b):
    return OR(AND(a, NOT(b)), AND(NOT(a), b))

def g_perbit(bit1, bit2):
    not_bit2 = NOT(bit2)
    return AND(bit1, not_bit2)

def e_perbit(bit1, bit2):
    return NOT(XOR(bit1, bit2))

def ge_perbit(bit1, bit2):
    not_bit1 = NOT(bit1)
    result = AND(not_bit1, bit2)
    return NOT(result)


def sum_perbit(bit1, bit2, carry_in):
    result = XOR(bit1, XOR(bit2, carry_in))
    carry_out = OR(AND(bit1, bit2), AND(XOR(bit1, bit2), carry_in))
    return result, carry_out

# little endian
def G_compare(x : list, y : list):
    result0 = ge_perbit(x[0], y[0])
    result1 = OR(g_perbit(x[1], y[1]), AND(e_perbit(x[1], y[1]), result0))
    result2 = OR(g_perbit(x[2], y[2]), AND(e_perbit(x[2], y[2]), result1))
    result3 = OR(g_perbit(x[3], y[3]), AND(e_perbit(x[3], y[3]), result2))
    result4 = OR(g_perbit(x[4], y[4]), AND(e_perbit(x[4], y[4]), result3))
    #result5 = OR(g_perbit(x[5], y[5]), AND(e_perbit(x[5], y[5]), result4))
    #result6 = OR(g_perbit(x[6], y[6]), AND(e_perbit(x[6], y[6]), result5))
    #return OR(g_perbit(x[7], y[7]), AND(e_perbit(x[7], y[7]), result6))
    return result4

# little endian
def G_sum(x : list, y : list):
    result0, carry0 = sum_perbit(x[0], y[0], 0)
    result1, carry1 = sum_perbit(x[1], y[1], carry0)
    result2, carry2 = sum_perbit(x[2], y[2], carry1)
    result3, carry3 = sum_perbit(x[3], y[3], carry2)
    result4, carry4 = sum_perbit(x[4], y[4], carry3)
    return [result0, result1, result2, result3, result4]
