#!/usr/bin/env python

<<<<<<< HEAD
from tests.test_files import TestFiles
import os
import json


def abs_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


with open(abs_path('data/primes-to-100k.txt'), 'r') as f:
    counter = 0
    for line in f:
        if not (counter % 10):
            prime = long(line.rstrip())
            print "Working with prime {}".format(prime)
            results = TestFiles.run_simulated_manually(
                'data/simulated.txt',
                universe_size=prime
            )
            c = results['stats']
            ti = results['uindex']
            print json.dumps(dict(
                stats=c.dict(),
                ratios=dict(
                    precision=c.get_precision(),
                    recall=c.get_recall()
                ),
                ti=ti
            ))
        counter += 1
=======
from math import sqrt
from tests.test_files import TestFiles
import json


def prime_numbers(mlim=100):
    """
    Prime number generator
    """
    for num in range(2, mlim + 1):
        if all(num % i != 0 for i in range(2, int(sqrt(num)) + 1)):
            yield num


counter = 0
for prime in prime_numbers(100000):
    if not (counter % 10):
        print "Working with prime {}".format(prime)
        results = TestFiles.run_simulated_manually(
            'data/simulated.txt',
            universe_size=prime
        )
        c = results['stats']
        ti = results['uindex']
        print json.dumps(dict(
            stats=c.dict(),
            ratios=dict(
                precision=c.get_precision(),
                recall=c.get_recall()
            ),
            ti=ti
        ))
    counter += 1
>>>>>>> 6d6e0de21b2eee7c2c34d326ff063ec4bc36ad31
