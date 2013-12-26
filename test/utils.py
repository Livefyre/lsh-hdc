"""
utils.py

Testing utilities
"""
import random
import operator


def randset():
    """Return a random set.  These values of n and k have wide-ranging
    similarities between pairs.
    """
    n = random.choice(range(5, 20))
    k = 10
    return tuple(set(random.choice(range(k)) for _ in range(n)))


def sigsim(x, y, dim):
    """Return the similarity of the two signatures"""
    return sum(map(operator.eq, x, y)) / float(dim)
