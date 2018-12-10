
import random

"""Functions that have to do with prime number operations"""
def is_prime (integer):
     for i in range (2, 1000):
        if integer % i == 0 and i != integer:
            return False 
        elif i >= integer//2:
            return True
        else:
            continue
prime = []
for i in range(2, 1000):
    if is_prime (i):
        prime.append(i)
def genPrime():
    return random.choice(prime)
    
def isPrimitiveRoot(g, n):
    """Checks that g is a primitive root of n"""
    modResults = set()
    for i in range(1,n):
        modResults.add((g**i)%n)
        if len(modResults) == n-1:
            return True
    return False

def random_primitive_root(n):
    primitive_root = []
    for i in range(n):
        if isPrimitiveRoot(i, n):
            primitive_root.append(i)
    return random.choice(primitive_root)



